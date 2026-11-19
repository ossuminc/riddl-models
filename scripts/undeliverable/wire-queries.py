#!/usr/bin/env python3
"""BACKLOG #43 step 4: give every undelivered query its channel, both ways.

Reid's ruling: the `GetRestaurantMenuItem` path in reactive-bbq's
MenuContext. For a queried processor T (entity or repository) in context C,
with app A connected to C:

  A  input <Q>Input acquires query <Q>          (one per query)
     outlet App<T>Queries  is query Q | type <T>Query
     inlet  App<T>Replies  is result R | type <T>Reply
  C  inlet  <T>QueriesIn / outlet <T>QueriesOut  + `forward` clause per query
     inlet  <T>RepliesIn / outlet <T>RepliesOut  + `send` relay per result
  T  inlet  <T>Queries / outlet <T>Replies   (+ `one of` types when >1)
  connectors: '<T>Query Stream' A->C (persistent, beside A's existing ones),
     '<T>Query Intake' C->T, '<T>Reply Egress' T->C, '<T>Reply Stream' C->A

REUSE, where the corpus already has the reply leg. Every dead result relay
(`msg-clause-undeliverable` on a context's `result R` clause) has one shape:
its inlet is fed by the context's REPOSITORY, which never answers R, while
exactly one ENTITY does. For such an entity the existing relay is kept and its
connector is repointed to come from the entity's new reply outlet; no fresh
reply ports are made. The repository outlet that fed it is then free: if the
repository has queries of its own it is RETYPED to what the repository answers
and becomes its reply outlet; if not it is left as it was and reported.

Works from `riddlc dump --json`. Text is inserted as whole lines before a
dump-located line (indent copied from that line; `sbt r` normalises it). The
two in-line edits -- a connector's `from outlet <ref>`, an outlet's type -- are
anchored on the dump's line for that node and refused if the text there does
not match exactly. A site that does not fit is REFUSED with a reason: a query
with no `replies`, a name already declared, no app connected to C, a result
relayed already but answered by a processor that also has another result.

Usage:  wire-queries.py [--apply] [--sweep FILE.jsonl] [model ...]
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()
PROCS = {"entity", "repository", "context", "projector", "adaptor", "streamlet"}


def words(ident):
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", ident)
    s = " ".join(p if p.isupper() and len(p) > 1 else p.lower() for p in parts)
    return s[:1].upper() + s[1:]


def lc(ident):
    return ident[:1].lower() + ident[1:]


def rel(path, scope):
    """`path` as referenced from inside `scope`: drop the common prefix with
    scope's PARENT, so a sibling of scope is named with scope's parent's
    child segment (Order.GetOrder from inside OrderContext.Order)."""
    p, b = path.split("."), scope.split(".")[:-1]
    i = 0
    while i < len(b) and i < len(p) - 1 and p[i] == b[i]:
        i += 1
    return ".".join(p[i:])


def desc(brief, text, ind="  "):
    return ["with {", f'{ind}briefly "{brief}"', f"{ind}described as {{",
            f"{ind}  |{text}", f"{ind}}}", "}"]


class Model:
    def __init__(self, model):
        self.model = model
        self.dir = ROOT / model
        conf = next(self.dir.glob("*.conf"))
        entry = re.search(r'input-file\s*=\s*"([^"]+)"', conf.read_text()).group(1)
        p = subprocess.run([str(RIDDLC), "dump", entry, "--json"], cwd=self.dir,
                           capture_output=True, text=True)
        if p.returncode != 0 or not p.stdout.strip():
            sys.exit(f"dump failed for {model}: {p.stderr[-400:]}")
        self.nodes = json.loads(p.stdout)
        self.byp = {n["path"]: n for n in self.nodes if "path" in n}
        self.kids = defaultdict(list)
        for n in self.nodes:
            self.kids[n.get("parent")].append(n)
        self.conn_to = defaultdict(list)
        self.conn_from = defaultdict(list)
        for n in self.nodes:
            if n["kind"] == "connector":
                self.conn_to[n["to"]["resolved"]].append(n)
                self.conn_from[n["from"]["resolved"]].append(n)
        self.declared = Counter(n.get("id") for n in self.nodes)
        self.ops = []  # (file, line, order, kind, payload)
        self.text = {}
        self.freed = set()
        self.retyped = set()

    # ---- facts
    def expand(self, alts, seen):
        out = set()
        for a in alts or []:
            r = a["resolved"]
            if r in seen:
                continue
            seen.add(r)
            t = self.byp.get(r)
            out |= self.expand(t["alternation"], seen) if t and t.get("alternation") else {r}
        return out

    def carries(self, port):
        t = port.get("type") or {}
        if t.get("alternation"):
            return self.expand(t["alternation"], set())
        tn = self.byp.get(t.get("resolved"))
        if tn and tn.get("alternation"):
            return self.expand(tn["alternation"], set())
        return {t.get("resolved")}

    def of(self, parent, kind):
        return [n for n in self.kids[parent] if n["kind"] == kind]

    def proc_of(self, n):
        for a in reversed(n.get("ancestors", [])):
            if self.byp.get(a, {}).get("kind") in PROCS:
                return self.byp[a]

    def ctx_of(self, n):
        for a in reversed(n.get("ancestors", [])):
            if self.byp.get(a, {}).get("kind") == "context":
                return self.byp[a]

    def replies(self, q):
        m = re.match(r"query replies result ([\w.]+)", q.get("type", ""))
        if not m:
            return None
        name = m.group(1)
        cands = [n for n in self.nodes if n["kind"] == "result"
                 and (n["path"].endswith("." + name) or n["id"] == name.split(".")[-1])]
        exact = [n for n in cands if n["path"].endswith("." + name)]
        pick = exact if len(exact) == 1 else cands
        if len(pick) == 1:
            return pick[0]["path"]
        near = [n for n in pick if n["parent"] == q["parent"]]
        return near[0]["path"] if len(near) == 1 else None

    def answered(self, proc):
        out = set()
        for n in self.nodes:
            if n["kind"] == "onmessageclause" and proc in n.get("ancestors", []):
                m = self.byp.get(n["message"]["resolved"])
                if m and m["kind"] == "query":
                    r = self.replies(m)
                    if r:
                        out.add(r)
        return out

    def line(self, n):
        return n["file"], n["span"]["start"]["line"]

    def first(self, nodes):
        return min(nodes, key=lambda n: n["span"]["start"]["offset"]) if nodes else None

    def claim(self, name):
        if self.declared[name]:
            return False
        self.declared[name] += 1
        return True

    # ---- edits
    def insert(self, at, lines, order=0):
        f, l = at
        self.ops.append((f, l, order, "insert", lines))

    def has(self, at, old):
        f, l = at
        if f not in self.text:
            self.text[f] = (self.dir / f).read_text().split("\n")
        return self.text[f][l - 1].count(old) == 1

    def replace(self, at, old, new):
        f, l = at
        self.ops.append((f, l, -1, "replace", (old, new)))

    def write(self):
        by_file = defaultdict(list)
        for op in self.ops:
            by_file[op[0]].append(op)
        for f, ops in by_file.items():
            p = self.dir / f
            text = p.read_text().split("\n")
            # bottom-up; at one line, replacements first, then inserts in order
            for _, l, order, kind, payload in sorted(ops, key=lambda o: (o[1], -o[2]), reverse=True):
                if kind == "replace":
                    old, new = payload
                    if text[l - 1].count(old) != 1:
                        raise SystemExit(f"{self.model}/{f}:{l}: expected one {old!r}")
                    text[l - 1] = text[l - 1].replace(old, new)
                else:
                    ind = re.match(r"\s*", text[l - 1]).group(0)
                    text[l - 1:l - 1] = [ind + x if x else x for x in payload]
            p.write_text("\n".join(text))


def plan_model(M, sites, refused, tally):
    # group the undelivered queries by target processor
    by_proc = defaultdict(list)
    for s in sites:
        cl = [n for n in M.nodes if n["kind"] == "onmessageclause"
              and n["file"].endswith(s["file"]) and n["span"]["start"]["line"] == s["line"]]
        if len(cl) != 1:
            refused.append((M.model, s["file"], s["line"], "clause not located")); continue
        q = M.byp.get(cl[0]["message"]["resolved"])
        T = M.proc_of(cl[0])
        if not q or q["kind"] != "query" or T["kind"] not in ("entity", "repository"):
            refused.append((M.model, s["file"], s["line"], "not an entity/repository query")); continue
        r = M.replies(q)
        if not r:
            refused.append((M.model, T["id"], q["id"], "query declares no (resolvable) `replies`")); continue
        if q["path"] not in [x[0] for x in by_proc[T["path"]]]:
            by_proc[T["path"]].append((q["path"], r))

    # the dead relays of each context: result -> (relay inlet, its connector)
    for Tpath, qs in sorted(by_proc.items(),
                            key=lambda kv: (M.byp[kv[0]]["kind"] != "entity", kv[0])):
        T = M.byp[Tpath]
        C = M.ctx_of(T)
        why = wire(M, T, C, qs, tally)
        if why:
            refused.append((M.model, T["id"], ",".join(q.split(".")[-1] for q, _ in qs), why))


def wire(M, T, C, qs, tally):
    tid, cid = T["id"], C["id"]
    queries = [q for q, _ in qs]
    results = sorted({r for _, r in qs})
    # the app connected to C, and where its connectors live
    apps = [n for n in M.nodes if n["kind"] == "context" and n.get("intention") == "Application"]
    app_conns = []
    for a in apps:
        for o in M.of(a["path"], "outlet"):
            for c in M.conn_from[o["path"]]:
                if c["to"]["resolved"].startswith(C["path"] + "."):
                    app_conns.append((a, c))
    if len({a["path"] for a, _ in app_conns}) != 1:
        return f"{len({a['path'] for a, _ in app_conns})} apps connected to {cid}"
    A, anchor_conn = app_conns[0][0], M.first([c for _, c in app_conns])
    groups = M.of(A["path"], "group")
    inputs = [n for n in M.nodes if n["kind"] == "input" and groups and n["parent"] == groups[0]["path"]]
    if not inputs:
        return f"app {A['id']} has no screen group with inputs"
    handlers = [h for h in M.of(C["path"], "handler")]
    handler = max(handlers, key=lambda h: len(M.kids[h["path"]]), default=None)
    clauses = [n for n in M.kids[handler["path"]]] if handler else []
    clauses = [n for n in clauses if n["kind"] in ("onmessageclause", "on-event")]
    if not clauses:
        return f"{cid} has no boundary handler with clauses"
    C_inlets, T_inlets = M.of(C["path"], "inlet"), M.of(T["path"], "inlet")
    A_outlets = M.of(A["path"], "outlet")
    if not (C_inlets and T_inlets and A_outlets):
        return "no inlet to anchor ports on"

    # REUSE: existing dead relays in C for T's results
    reuse = {}
    for r in results:
        for i in C_inlets:
            if r in M.carries(i):
                feeders = M.conn_to[i["path"]]
                relay = [n for n in clauses if n["kind"] == "onmessageclause"
                         and n["message"]["resolved"] == r]
                if len(feeders) == 1 and relay:
                    src_outlet = M.byp.get(feeders[0]["from"]["resolved"], {})
                    src = M.byp.get(src_outlet.get("parent"), {})
                    if src.get("path") != T["path"] and r not in M.answered(src.get("path", "")):
                        reuse[r] = (i, feeders[0], src_outlet, src)
    # T's OWN reply leg, already complete: an outlet of T carrying all its
    # results, connected into C, where every result has a relay clause
    def relayed(r):
        return any(n["kind"] == "onmessageclause" and n["message"]["resolved"] == r for n in clauses)
    own = [o for o in M.of(T["path"], "outlet") if set(results) <= M.carries(o)
           and any(c["to"]["resolved"].startswith(C["path"] + ".") for c in M.conn_from[o["path"]])
           and all(relayed(r) for r in results)]
    if own:
        tally["own reply leg reused"] += 1
    # a result the context already relays (from another processor) converges
    # in that relay clause: the handler dispatches on type, not inlet
    relay_new = [r for r in results if not relayed(r)]
    if reuse and len(results) != 1 and not own:
        return "a result is relayed already, but this processor answers several"
    if reuse and T["kind"] == "repository":
        return "repository's result is relayed from another repository"

    for r, v in reuse.items():
        i, conn, src_outlet, src = v
        if not M.has(M.line(conn), f"from outlet {conn['from']['ref']}"):
            return f"relay connector {conn['id']}: `from outlet` text is not on its line"
    # names
    names = {
        "Tq": f"{tid}Queries", "Tr": f"{tid}Replies",
        "Cqi": f"{tid}QueriesIn", "Cqo": f"{tid}QueriesOut",
        "Cri": f"{tid}RepliesIn", "Cro": f"{tid}RepliesOut",
        "Aq": f"App{tid}Queries", "Ar": f"App{tid}Replies",
        "Kqs": f"{tid}Query Stream", "Kqi": f"{tid}Query Intake",
        "Kre": f"{tid}Reply Egress", "Krs": f"{tid}Reply Stream",
        "Qt": f"{tid}Query", "Rt": f"{tid}Reply",
    }
    retype = None  # a freed repository outlet to reuse as T's reply outlet
    if T["kind"] == "repository":
        # was any of this repository's outlets freed by an entity's repoint?
        freed = [o for o in M.of(T["path"], "outlet") if o["path"] in M.freed]
        if len(freed) == 1:
            retype = freed[0]
    need = ["Tq", "Cqi", "Cqo", "Aq", "Kqs", "Kqi"]
    if not retype and not own:
        need.append("Tr")
    if own:
        reuse = dict(reuse) or {"__own__": None}
    if not reuse:
        need += ["Cri", "Kre"] + (["Cro", "Ar", "Krs"] if relay_new else [])
    elif retype is None and False:
        pass
    if len(queries) > 1:
        need.append("Qt")
    if len(results) > 1:
        need.append("Rt")
    for k in need:
        if M.declared[names[k]] and not M.declared[names[k] + "Port"]:
            names[k] += "Port"
    clash = [names[k] for k in need if M.declared[names[k]]]
    for q in queries:
        if M.declared[q.split(".")[-1] + "Input"]:
            clash.append(q.split(".")[-1] + "Input")
    if clash:
        return "name already declared: " + ", ".join(clash)
    for k in need:
        M.claim(names[k])
    for q in queries:
        M.claim(q.split(".")[-1] + "Input")

    Tp, Cp, Ap = T["path"], C["path"], A["path"]
    tw = words(tid).lower()
    # --- T: types and ports
    t_at = M.line(M.first(T_inlets))
    t_lines = []
    if len(queries) > 1:
        t_lines += [f"type {names['Qt']} is one of {{",
                    "  " + " or ".join(rel(q, Tp + ".x") for q in queries),
                    "} " + desc(f"What may be asked of {tid}", f"The look-ups the {tw} answers.")[0]] \
            + desc(f"What may be asked of {tid}", f"The look-ups the {tw} answers.")[1:]
    if len(results) > 1:
        t_lines += [f"type {names['Rt']} is one of {{",
                    "  " + " or ".join(rel(r, Tp + ".x") for r in results),
                    "} " + desc(f"What {tid} answers", f"The answers the {tw} gives.")[0]] \
            + desc(f"What {tid} answers", f"The answers the {tw} gives.")[1:]
    q_ty = (f"type {names['Qt']}" if len(queries) > 1 else f"query {rel(queries[0], Tp + '.x')}")
    r_ty_T = (f"type {names['Rt']}" if len(results) > 1 else f"result {rel(results[0], Tp + '.x')}")
    t_lines += [f"inlet {names['Tq']} is {q_ty} " + "with {",
                f'  briefly "Look-ups of this {tw}"', "  described as {",
                f"    |What {A['id']} asks of the {tw}, by way of {cid}.", "  }", "}"]
    if retype:
        old_ty = retype["type"]["ref"]
        kw = retype["type"].get("carries", "").lower()
        old = next((o for o in (f"is {kw} {old_ty}", f"is type {old_ty}") if M.has(M.line(retype), o)), None)
        if old is None:
            return f"freed outlet {retype['id']}: its type text is not on its line"
        M.replace(M.line(retype), old, f"is {r_ty_T}")
        M.retyped.add(retype["path"])
        names["Tr"] = retype["id"]
        tally["repository outlet retyped"] += 1
    elif not own:
        t_lines += [f"outlet {names['Tr']} is {r_ty_T} " + "with {",
                    f'  briefly "This {tw}\'s answers"', "  described as {",
                    f"    |What the {tw} answers, on its way back to {cid}.", "  }", "}"]
    M.insert(t_at, t_lines)

    # --- C: ports, clauses, intra connectors
    cq_ty = (f"type {rel(Tp + '.' + names['Qt'], Cp + '.x')}" if len(queries) > 1
             else f"query {rel(queries[0], Cp + '.x')}")
    cr_ty = (f"type {rel(Tp + '.' + names['Rt'], Cp + '.x')}" if len(results) > 1
             else f"result {rel(results[0], Cp + '.x')}")
    c_lines = [f"inlet {names['Cqi']} is {cq_ty} with {{", f'  briefly "Look-ups of the {tw}"',
               "  described as {", f"    |{A['id']}'s look-ups, on their way to the {tw}.", "  }", "}",
               f"outlet {names['Cqo']} is {cq_ty} with {{", f'  briefly "Look-ups on their way to the {tw}"',
               "  described as {", f"    |Each look-up goes to the {tw} it names.", "  }", "}"]
    if not reuse:
        c_lines += [f"inlet {names['Cri']} is {cr_ty} with {{", f'  briefly "The {tw}\'s answers"',
                    "  described as {", f"    |What the {tw} answers about itself.", "  }", "}"]
    if not reuse and relay_new:
        c_lines += [f"outlet {names['Cro']} is {cr_ty} with {{", f'  briefly "Answers to {A["id"]}"',
                    "  described as {", f"    |The reply leg of {A['id']}'s look-ups of the {tw}.", "  }", "}"]
    M.insert(M.line(M.first(C_inlets)), c_lines)

    cl_lines = []
    for q in queries:
        b = lc(q.split(".")[-1])
        cl_lines += [f"on {b}: query {rel(q, Cp + '.x')} is {{",
                     f"  forward {b} to outlet {cid}.{names['Cqo']}", "}"]
    if not reuse:
        for r in relay_new:
            b = lc(r.split(".")[-1])
            cl_lines += [f"on {b}: result {rel(r, Cp + '.x')} is {{",
                         f"  send {b} to outlet {cid}.{names['Cro']}", "}"]
    M.insert(M.line(M.first(clauses)), cl_lines)

    c_conns = [n for n in M.of(Cp, "connector")]
    k_at = M.line(M.first(c_conns)) if c_conns else M.line(handler)
    k_lines = [f"connector '{names['Kqi']}' is from outlet {cid}.{names['Cqo']} "
               f"to inlet {cid}.{rel(Tp, Cp + '.x')}.{names['Tq']} with {{",
               f'  briefly "Look-ups on their way to the {tw}"', "}"]
    if not reuse:
        k_lines += [f"connector '{names['Kre']}' is from outlet {cid}.{rel(Tp, Cp + '.x')}.{names['Tr']} "
                    f"to inlet {cid}.{names['Cri']} with {{",
                    f'  briefly "The {tw}\'s answers on their way to the boundary"', "}"]
    M.insert(k_at, k_lines)

    # --- reuse: repoint the dead relay's connector to come from T
    for r, v in reuse.items():
        if v is None:
            continue
        i, conn, src_outlet, src = v
        f, l = M.line(conn)
        old = f"from outlet {conn['from']['ref']}"
        M.replace((f, l), old, f"from outlet {cid}.{rel(Tp, Cp + '.x')}.{names['Tr']}")
        M.freed.add(src_outlet["path"])
        tally["relay repointed"] += 1

    # --- A: inputs, ports, domain connectors
    for q in queries:
        qn = q.split(".")[-1]
        M.insert(M.line(M.first(inputs)), [
            f"input {qn}Input acquires query {rel(q, Ap + '.x')} with {{",
            f'  briefly "{words(qn)} control"', "  described as {",
            f"    |The control through which a user asks the {words(qn).lower()} question.", "  }", "}"])
    aq_ty = (f"type {rel(Tp + '.' + names['Qt'], Ap + '.x')}" if len(queries) > 1
             else f"query {rel(queries[0], Ap + '.x')}")
    ar_ty = (f"type {rel(Tp + '.' + names['Rt'], Ap + '.x')}" if len(results) > 1
             else f"result {rel(results[0], Ap + '.x')}")
    a_lines = [f"outlet {names['Aq']} is {aq_ty}"]
    if not reuse and relay_new:
        a_lines += [f"inlet {names['Ar']} is {ar_ty}"]
    M.insert(M.line(M.first(A_outlets)), a_lines)
    dom = M.byp[anchor_conn["parent"]]["path"]
    d_lines = [f"persistent connector '{names['Kqs']}' is from outlet {rel(Ap, dom + '.x')}.{names['Aq']} "
               f"to inlet {rel(Cp, dom + '.x')}.{names['Cqi']} with {{",
               f'  briefly "{A["id"]}\'s look-ups of the {tw}"', "}"]
    if not reuse and relay_new:
        d_lines += [f"persistent connector '{names['Krs']}' is from outlet {rel(Cp, dom + '.x')}.{names['Cro']} "
                    f"to inlet {rel(Ap, dom + '.x')}.{names['Ar']} with {{",
                    f'  briefly "The {tw}\'s answers returned to {A["id"]}"', "}"]
    M.insert(M.line(anchor_conn), d_lines)
    tally["processors wired"] += 1
    tally["queries wired"] += len(queries)
    tally["entity" if T["kind"] == "entity" else "repository"] += 1
    return None


def main():
    argv = sys.argv[1:]
    apply = "--apply" in argv
    sweep = argv[argv.index("--sweep") + 1] if "--sweep" in argv else None
    only = {a.rstrip("/") for a in argv if not a.startswith("--") and a != sweep}
    if not sweep:
        sys.exit("--sweep FILE.jsonl is required (collect-warnings.py output)")
    sites = defaultdict(list)
    for x in map(json.loads, open(sweep)):
        if x["rule"] == "msg-clause-undeliverable" and re.search(
                r"of (Entity|Repository) '[^']*' handles Query", x["message"]):
            if not only or x["model"] in only:
                sites[x["model"]].append(x)
    tally, refused = Counter(), []
    for model, ss in sorted(sites.items()):
        M = Model(model)
        # entities first, so repositories see the outlets their repoints free
        def key(s):
            return 0 if "of Entity" in s["message"] else 1
        plan_model(M, sorted(ss, key=key), refused, tally)
        for o in sorted(M.freed - M.retyped):
            refused.append((model, o, "", "freed repository outlet left as it was (repository has no undelivered query)"))
        if apply:
            M.write()
        tally["models"] += 1
    for k, v in sorted(tally.items()):
        print(f"{v}\t{k}", file=sys.stderr)
    print(f"{len(refused)}\trefused", file=sys.stderr)
    for x in refused:
        print("REFUSED\t" + "\t".join(str(y) for y in x))


if __name__ == "__main__":
    main()
