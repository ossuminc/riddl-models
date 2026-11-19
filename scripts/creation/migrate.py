#!/usr/bin/env python3
"""Move every stateful entity to riddl 2.8.0's creation model.

The context creates; the entity's entity-level `on init(args)` morphs it into
its starting state (Reid's ruling (B), 2026-11-18, applied to patterns/ in
94a1b4480 and to reactive-bbq in 7e1ff5bc2). riddlc 2.7.0-20 reports the old
shape as `entity-init-in-state` and `entity-init-no-morph`.

Per entity, with S0 its first declared state:

  event-sourced -- S0's on init yields the creation event E; E's fold morphs;
    one command clause CC yields E.
      on init(<E's fields but the id>) = the fold's body, each `e.f` read as
      the argument f and the id as `self.id`
  CRUD -- one command clause CC morphs into S0.
      on init(<the fields of C that CC reads, but the id>) = CC's body, each
      `c.f` read as the argument f and the id as `self.id`

Then: every old `on init` goes (a handler left empty goes with it), CC and
the fold go, and the context's boundary clause for C creates the entity,
passing what CC passed. An event-sourced creator also yields E there, with
the new id, as the answer to whoever asked (C declares `yields event E`).

Anything not exactly one of those shapes is reported, not guessed at.

Usage:
    ./scripts/creation/migrate.py [--apply] [model-dir ...]
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()


class Skip(Exception):
    pass


KEYWORDS = {"result", "event", "command", "query", "type", "record", "state",
            "entity", "context", "handler", "on", "is", "of", "to", "from",
            "with", "yield", "reply", "send", "tell", "morph", "become", "set",
            "let", "when", "then", "else", "end", "error", "do", "init", "self",
            "empty", "true", "false", "inlet", "outlet", "domain", "function",
            "call", "ask", "create", "foreach", "append", "remove", "log", "store",
            "update", "delete", "upsert", "prompt", "system", "forward", "in",
            "where", "and", "or", "not", "become", "stop", "focus", "any", "all"}


CREATE_VERBS = (r"(Create|Register|Open|Start|Submit|Initiate|Add|Place|New|Apply|"
                r"Establish|Enroll|Onboard|Provision|Install|Commission|Plan|Record|"
                r"Request|Schedule|File|Issue|Receive|Report|Initialize|Init|Define|"
                r"Draft|Book|Admit|Acquire|Launch)[A-Z]")


STRONG_CREATE_VERBS = (r"(Create|Register|Open|Start|Initiate|New|Add|Establish|"
                       r"Onboard|Provision|Enroll|Admit|Submit|Apply)[A-Z]")


def pname(f):
    """An on-init parameter name for field f; a keyword cannot be one."""
    return f + "Value" if f in KEYWORDS else f


def models():
    for conf in sorted(ROOT.rglob("*.conf")):
        rel = conf.parent.relative_to(ROOT)
        if rel.parts and rel.parts[0] in ("patterns", "project", "target", "scripts"):
            continue
        if conf.stem == conf.parent.name and (conf.parent / (conf.stem + ".riddl")).exists():
            yield conf.parent


def dump(mdir):
    out = subprocess.run([str(RIDDLC), "dump", mdir.name + ".riddl", "--json"],
                         cwd=mdir, capture_output=True, text=True)
    if not out.stdout.strip():
        raise SystemExit(f"dump failed: {mdir}\n{out.stderr[-400:]}")
    return json.loads(out.stdout)


def under(path, prefix):
    return path == prefix or path.startswith(prefix + ".")


def split_args(text):
    """'a = x, b = f(y, "z,")' -> {'a': 'x', 'b': 'f(y, "z,")'}; top level only."""
    out, depth, cur, q = [], 0, "", False
    for ch in text:
        if q:
            cur += ch
            if ch == '"':
                q = False
            continue
        if ch == '"':
            q = True
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    args = {}
    for a in out:
        k, _, v = a.partition("=")
        args[k.strip()] = v.strip()
    return args


def ctor_args(stmt_text):
    """The argument text of the first constructor in a statement."""
    i = stmt_text.index("(")
    depth, q = 0, False
    for j in range(i, len(stmt_text)):
        ch = stmt_text[j]
        if q:
            q = ch != '"'
            continue
        if ch == '"':
            q = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return stmt_text[i + 1:j]
    raise Skip("unbalanced constructor")


def body_of(clause_text):
    """Statements inside an 'on ... is { ... }' clause."""
    i = clause_text.index("{")
    j = clause_text.rindex("}")
    return clause_text[i + 1:j].strip()


class Model:
    def __init__(self, mdir):
        self.dir = mdir
        self.nodes = dump(mdir)
        self.by_path = {n["path"]: n for n in self.nodes if "path" in n}
        self.kids = defaultdict(list)
        for n in self.nodes:
            self.kids[n.get("parent", "")].append(n)
        self.src = {}
        self.edits = defaultdict(list)
        self.renames = []
        self.drops = []  # (constructor head, field) -- an argument C lost

    def text(self, n):
        f = n["file"]
        if f not in self.src:
            self.src[f] = (self.dir / f).read_text()
        s = self.src[f]
        return s[n["span"]["start"]["offset"]:n["span"]["end"]["offset"]]

    def fields(self, path):
        return [n for n in self.kids[path] if n["kind"] == "field"]

    def type_text(self, field):
        """The field's type as written: 'Currency(USD)', not 'Currency'."""
        t = self.text(field)
        t = t[t.index(":") + 1:]
        cut = len(t)
        for stop in (" with {", " with{", "\n"):
            i = t.find(stop)
            if i >= 0:
                cut = min(cut, i)
        return t[:cut].strip()

    def is_id_of(self, field, ent):
        t = field.get("type", "")
        if not t.startswith("type "):
            return False
        name = t[5:]
        for n in self.nodes:
            if n["kind"] == "type" and n["id"] == name.split(".")[-1] \
                    and re.fullmatch(rf"Id\((?:[\w.]+\.)?{ent['id']}\)", n.get("type", "")):
                return True
        return False

    def edit(self, n, new):
        self.edits[n["file"]].append((n["span"]["start"]["offset"],
                                      n["span"]["end"]["offset"], new))


def synth_morph(m, ent, ctx, s0, have, id_field):
    head = m.text(s0)
    mm = re.match(r"\s*state\s+\w+\s+(?:of|is)\s+(?:record\s+)?([\w.]+)", head)
    if not mm:
        raise Skip("cannot read the starting state's record")
    name = mm.group(1).split(".")[-1]
    recs = [n for n in m.nodes if n["kind"] in ("record", "type") and n.get("id") == name]
    near = [r for r in recs if under(ent["path"], r["parent"])]
    rec = max(near, key=lambda r: len(r["parent"])) if near else (recs[0] if len(recs) == 1 else None)
    if not rec:
        raise Skip(f"record {name} unresolved")
    args = []
    for f in m.fields(rec["path"]):
        if f["id"] == id_field or m.is_id_of(f, ent):
            args.append(f"{f['id']} = self.id")
        elif f["id"] in have:
            args.append(f"{f['id']} = {pname(f['id'])}")
        elif f.get("acceptsEmpty"):
            args.append(f"{f['id']} = empty")
        else:
            words = re.sub(r"(?<=[a-z0-9])([A-Z])", r" \1", f["id"]).lower()
            args.append(f'{f["id"]} = prompt("the {words} a new {ent["id"]} starts with")')
    ref = mm.group(1)
    return (f"morph entity {ctx['id']}.{ent['id']} to state {ctx['id']}.{ent['id']}.{s0['id']} "
            f"with record {ref}(" + ", ".join(args) + ")")


def migrate_entity(m, ent):
    ep = ent["path"]
    ctx = m.by_path[ent["parent"]]
    states = sorted([n for n in m.nodes if n["kind"] == "state" and n["parent"] == ep],
                    key=lambda s: (s["file"], s["span"]["start"]["offset"]))
    if not states:
        return None
    s0 = states[0]
    inits = [n for n in m.nodes if n["kind"] == "on-init" and under(n["parent"], ep)]
    # already in the creation model: an entity-level on init that morphs
    if any(m.by_path[i["parent"]]["parent"] == ep
           and any(k["kind"] == "morph-statement" for k in m.kids[i["path"]]) for i in inits):
        return None
    clauses = [n for n in m.nodes if n["kind"] == "onmessageclause"
               and under(n["parent"], ep) and n["id"].startswith("command ")]
    s0_inits = [i for i in inits if under(i["parent"], s0["path"])]
    event = None
    if s0_inits:
        lets = [n for n in m.kids[s0_inits[0]["path"]] if n["kind"] == "let-statement"]
        if lets and lets[0].get("declaredType"):
            event = lets[0]["declaredType"].get("resolved")
            if m.by_path.get(event, {}).get("kind") != "event":
                event = None

    fold = None
    if event:
        def yields_event(c):
            kids = m.kids[c["path"]]
            if any(y["kind"] == "yield-statement"
                   and y.get("message", {}).get("resolved") == event for y in kids):
                return True
            # 'let e: type E = prompt(...)' then 'yield e'
            bound = {k.get("binds") for k in kids if k["kind"] == "let-statement"
                     and k.get("declaredType", {}).get("resolved") == event}
            return any(y["kind"] == "yield-statement"
                       and y.get("message", {}).get("value") in bound for y in kids)
        cc = [c for c in clauses if yields_event(c)]
        folds = [n for n in m.nodes if n["kind"] == "on-event" and under(n["parent"], ep)
                 and n.get("message", {}).get("resolved") == event]
        if len(cc) != 1 or len(folds) != 1:
            raise Skip(f"event-sourced: {len(cc)} creators, {len(folds)} folds of "
                       f"{event.rsplit('.', 1)[-1]}")
        cc, fold = cc[0], folds[0]
        synth = not any(n["kind"] == "morph-statement" for n in m.kids[fold["path"]])
    else:
        def enters_s0(st):
            if st["kind"] == "morph-statement":
                return st.get("state", {}).get("resolved") == s0["path"]
            # a single-state entity's 'set state S to record R(...)'
            return (st["kind"] == "set-statement" and st.get("target") == s0["id"]
                    and isinstance(st.get("value"), dict) and "resolved" in st["value"])
        cc = [c for c in clauses if any(enters_s0(st) for st in m.kids[c["path"]])]
        if not cc:
            # nothing enters the first-declared state; the one creating command
            # that morphs at all names the state an instance really starts in
            made = [c for c in clauses
                    if re.match(CREATE_VERBS, c["id"].split(" ", 1)[1].split(".")[-1])
                    and any(st["kind"] == "morph-statement" for st in m.kids[c["path"]])]
            order = [st["path"] for st in states]

            def target(c):
                t = [st for st in m.kids[c["path"]]
                     if st["kind"] == "morph-statement"][0]["state"].get("resolved")
                return order.index(t) if t in order else len(order)
            made.sort(key=target)
            # several may morph (renew, churn); the one entering the earliest
            # declared state is where an instance begins
            if made and (len(made) == 1 or target(made[0]) < target(made[1])) \
                    and target(made[0]) < len(order):
                s0 = states[target(made[0])]
                cc = [made[0]]
        synth_crud = False
        if not cc:
            # a creating command that never puts the instance in a state
            # (CreateTeam yields TeamCreated, whose fold is prose): it still
            # creates, and the morph is built from what it carries
            named = [c for c in clauses
                     if re.match(STRONG_CREATE_VERBS, c["id"].split(" ", 1)[1].split(".")[-1])
                     and not any(st["kind"] in ("morph-statement", "set-statement")
                                 for st in m.kids[c["path"]])]
            if len(named) == 1:
                cc, synth_crud = named, True
        if len(cc) > 1:
            # one creates; the others return an existing instance to S0
            made = [c for c in cc if re.match(CREATE_VERBS, c["id"].split(" ", 1)[1].split(".")[-1])]
            if len(made) == 1:
                cc = made
        if len(cc) != 1:
            raise Skip(f"CRUD: {len(cc)} command clauses morph into {s0['id']}")
        cc = cc[0]
    cmd = m.by_path.get(cc.get("message", {}).get("resolved", ""))
    if not cmd:
        raise Skip("creating command unresolved")
    if len([f for f in m.fields(cmd["path"]) if not m.is_id_of(f, ent)]) == 0 \
            and not re.match(CREATE_VERBS, cmd["id"]):
        raise Skip(f"{cmd['id']} carries nothing but the id, so it creates nothing")
    # an unbound clause reads its message by name: 'StartRun.generationRunId'
    cc_bind = cc.get("binding") or cmd["id"]

    # what the creator passes, field by field, as text in terms of cc_bind
    cmd_fields = m.fields(cmd["path"])
    cmd_id = [f["id"] for f in cmd_fields if m.is_id_of(f, ent)]
    if fold:
        ev = m.by_path[event]
        ev_fields = m.fields(event)
        ev_id = [f["id"] for f in ev_fields if m.is_id_of(f, ent)]
        if len(ev_id) != 1:
            raise Skip(f"creation event has {len(ev_id)} id fields")
        yields = [y for y in m.kids[cc["path"]] if y["kind"] == "yield-statement"]
        if yields[0].get("message", {}).get("resolved") == event:
            passed = split_args(ctor_args(m.text(yields[0])))
        else:
            # the creator prompted for the whole event; ask for each field
            words = lambda f: re.sub(r"(?<=[a-z0-9])([A-Z])", r" \1", f).lower()
            passed = {f["id"]: f'prompt("the {words(f["id"])} of the new {ent["id"]}")'
                      for f in m.fields(event)}
        params = [(f["id"], m.type_text(f)) for f in ev_fields if f["id"] != ev_id[0]]
        args = {p: passed.get(p) for p, _ in params}
        missing = [p for p, v in args.items() if v is None]
        if missing:
            raise Skip(f"creator yield omits {missing}")
        fb = fold.get("binding")
        if synth:
            # the fold states nothing a replay can use (prose sets, a resend):
            # build the starting record from the creation data by field name
            body = synth_morph(m, ent, ctx, s0, {p for p, _ in params}, ev_id[0])
            fb = fb or "_"
        else:
            body = body_of(m.text(fold))
        if not fb:
            raise Skip("fold has no binding")
        body = re.sub(rf"\b{fb}\.{ev_id[0]}\b", "self.id", body)
        body = re.sub(rf"\b{fb}\.(\w+)", lambda mm: pname(mm.group(1)), body)
        if re.search(rf"\b{fb}\b", body):
            raise Skip("fold reads the whole event")
    else:
        body = body_of(m.text(cc))
        if synth_crud:
            # it read the whole command's fields; every non-id one is an argument
            body = (f"__MORPH__\n" + body)
        # nothing else puts a new instance in a state, so the set is a morph
        body = re.sub(rf"\bset state {s0['id']} to record ",
                      f"morph entity {ctx['id']}.{ent['id']} to state "
                      f"{ctx['id']}.{ent['id']}.{s0['id']} with record ", body)
        if len(cmd_id) > 1:
            raise Skip("creating command has several ids")
        if cmd_id:
            body = re.sub(rf"\b{cc_bind}\.{cmd_id[0]}\b", "self.id", body)
        used = sorted(set(re.findall(rf"\b{cc_bind}\.(\w+)", body))
                      | ({f["id"] for f in cmd_fields if f["id"] not in cmd_id} if synth_crud else set()),
                      key=[f["id"] for f in cmd_fields].index)
        ftype = {f["id"]: m.type_text(f) for f in cmd_fields}
        params = [(f, ftype[f]) for f in used]
        args = {f: f"{cc_bind}.{f}" for f in used}
        body = re.sub(rf"\b{cc_bind}\.(\w+)", lambda mm: pname(mm.group(1)), body)
        if re.search(rf"\b{cc_bind}\b", body):
            raise Skip("creator reads the whole command")
        if not params and not re.match(CREATE_VERBS, cmd["id"]):
            raise Skip("creator reads no fields of its command")
        if synth_crud:
            body = body.replace("__MORPH__", synth_morph(
                m, ent, ctx, s0, {p for p, _ in params}, cmd_id[0] if cmd_id else ""))

    # the context's boundary clause for C
    relays = [n for n in m.nodes if n["kind"] == "onmessageclause"
              and n["parent"].rsplit(".", 1)[0] == ctx["path"]
              and m.by_path[n["parent"]]["kind"] == "handler"
              and n.get("message", {}).get("resolved") == cmd["path"]]
    if len(relays) > 1:
        raise Skip(f"{len(relays)} boundary clauses for {cmd['id']}")
    relay = relays[0] if relays else None
    if relay is None:
        # nothing at the boundary handled C: the creating clause goes beside
        # the context's other relays
        bounds = [h for h in m.nodes if h["kind"] == "handler" and h["parent"] == ctx["path"]
                  and any(k["kind"] == "onmessageclause" for k in m.kids[h["path"]])]
        if len(bounds) != 1:
            raise Skip(f"no boundary clause for {cmd['id']}, and {len(bounds)} boundary handlers")
    rb = (relay.get("binding") if relay else None) or cmd["id"][0].lower() + cmd["id"][1:]
    relay_kinds = {k["kind"] for k in m.kids[relay["path"]] if k["kind"].endswith("-statement")} \
        if relay else set()
    if not relay_kinds <= {"forward-statement", "send-statement", "tell-statement"}:
        raise Skip(f"boundary clause does more than relay: {sorted(relay_kinds)}")

    def rebind(v):
        return re.sub(rf"\b{cc_bind}\b", rb, v)

    move_command(m, ent, ctx, cmd, cmd_id, relay)

    new_var = "new" + ent["id"]
    # a value the creator only prompts for is asked once, not once for the
    # create and again for the event (a let cannot hold a collection)
    ids = {n.get("id") for n in m.nodes}
    lets = []
    ptype = dict(params)
    for p, _ in params:
        v = args[p]
        t = ptype[p]
        if fold and v.startswith("prompt(") and not t.endswith(("+", "*", "?")):
            name = "given" + p[0].upper() + p[1:]
            if name in ids:
                continue
            lets.append(f"let {name}: {t if t.startswith('type ') else 'type ' + t} = {v}")
            args[p] = name
    create = (f"let {new_var} = create entity {ctx['id']}.{ent['id']}("
              + ", ".join(f"{p} = {rebind(args[p])}" for p, _ in params) + ")")
    ctx_body = lets + [create]
    if fold:
        ev_args = [f"{ev_id[0]} = {new_var}"] + [f"{p} = {rebind(args[p])}" for p, _ in params]
        ctx_body.append(f"yield event {ent['id']}.{ev['id']}(" + ", ".join(ev_args) + ")")
    else:
        ctx_body.append(f"log {new_var}")
    if relay:
        head = m.text(relay)
        head = head[:head.index("{") + 1]
        m.edit(relay, head + "\n" + "\n".join(ctx_body) + "\n}\n")
    else:
        b = bounds[0]
        at = b["span"]["start"]["offset"] + m.text(b).index("{") + 1
        m.edits[b["file"]].append((at, at, f"\non {rb}: command {ent['id']}.{cmd['id']} is {{\n"
                                   + "\n".join(ctx_body) + "\n}\n"))

    # the entity side. An event-sourced entity published its creation event
    # on its outlet when it yielded it; now the context yields it, so on init
    # sends it there for the stores and projections (reactive-bbq 7e1ff5bc2)
    if fold:
        outs = [n for n in m.nodes if n["kind"] == "outlet" and n["parent"] == ep
                and isinstance(n.get("type"), dict)
                and (n["type"].get("resolved") == event
                     or any(a.get("resolved") == event
                            for a in n["type"].get("alternation", [])))]
        if len(outs) > 1:
            raise Skip(f"{len(outs)} outlets carry {ev['id']}")
        if outs:
            ev_vals = [f"{ev_id[0]} = self.id"] + [f"{p} = {pname(p)}" for p, _ in params]
            body += (f"\nsend event {ev['id']}(" + ", ".join(ev_vals) + ") to outlet "
                     f"{ctx['id']}.{ent['id']}.{outs[0]['id']}")
    sig = ("(" + ", ".join(f"{pname(p)}: {t}" for p, t in params) + ")") if params else ""
    on_init = ("on init" + sig + " is {\n"
               + body + "\n}\n")
    handlers = [n for n in m.nodes if n["kind"] == "handler" and n["parent"] == ep]
    if handlers:
        h = handlers[0]
        h_text = m.text(h)
        first = h_text.index("{") + 1
        m.edits[h["file"]].append((h["span"]["start"]["offset"] + first,
                                   h["span"]["start"]["offset"] + first, "\n" + on_init))
    else:
        e_text = m.text(ent)
        first = ent["span"]["start"]["offset"] + e_text.index("{") + 1
        m.edits[ent["file"]].append((first, first,
            f"\nhandler {ent['id']}Creation is {{\n{on_init}}} with {{\n"
            f"  briefly \"{ent['id']} creation\"\n  described as {{\n"
            f"    |Puts a new {ent['id']} in its starting state.\n  }}\n}}\n"))
    for n in [cc] + ([fold] if fold else []):
        m.edit(n, "")
    for i in inits:
        hh = m.by_path[i["parent"]]
        rest = [k for k in m.kids[hh["path"]] if k is not i and k["kind"] not in ("linecomment",)
                and k["kind"] in ("onmessageclause", "on-event", "on-other", "on-init")
                or (k is not i and k["kind"].startswith("on"))]
        rest = [k for k in rest if k not in (cc, fold)]
        if not rest and hh["parent"] != ep:
            m.edit(hh, "")
        else:
            m.edit(i, "")
    return (f"{ent['id']}: {'event-sourced' if fold else 'CRUD'}, {cmd['id']} creates "
            f"via {ctx['id']}, on init({', '.join(p for p, _ in params)})")


def move_command(m, ent, ctx, cmd, cmd_id, relay):
    """C becomes a request to the context (reactive-bbq d9b975949).

    The entity no longer handles C, so it leaves the entity -- minus its id,
    which create mints -- and the entity's alternation. A context-level
    <X>Request alternation carries C beside the entity's commands, and every
    port outside the entity that carried the entity alternation carries it
    instead, except those feeding the entity itself.
    """
    ep, X, Ctx = ent["path"], ent["id"], ctx["id"]
    alts = [n for n in m.nodes if n["kind"] == "type" and n["parent"] == ep
            and "one of" in n.get("type", "")
            and re.search(rf"\b{re.escape(cmd['id'])}\b", n.get("type", ""))]
    if len(alts) != 1:
        raise Skip(f"{cmd['id']} is in {len(alts)} alternations")
    alt = alts[0]
    members = re.findall(r"type ([\w.]+)", alt["type"])
    if len(members) < 2:
        raise Skip(f"{alt['id']} would be left with no member")
    req = f"{X}Request"
    if any(n.get("id") == req for n in m.nodes):
        req = f"{X}CreationRequest"
    if any(n.get("id") == req for n in m.nodes):
        raise Skip(f"{req} already exists")
    # the definition, moved
    ctext = m.text(cmd)
    for f in m.fields(cmd["path"]):
        if f["id"] in cmd_id:
            ctext = ctext.replace(m.text(f), "", 1)
    if all(f["id"] in cmd_id for f in m.fields(cmd["path"])):
        # nothing left but the id create mints: an empty body is '???'
        i = ctext.index("{")
        j = ctext.index("}", i) if "with {" not in ctext[i:] else None
        body_end = ctext.rindex("} with {") if "} with {" in ctext else ctext.rindex("}")
        ctext = ctext[:i + 1] + " ??? " + ctext[body_end:]
    local = {n["id"] for n in m.nodes if n.get("parent") == ep
             and n["kind"] in ("type", "record", "event", "command", "query", "result")}
    ctext = re.sub(r"(yields event )(\w+)\b",
                   lambda mm: mm.group(1) + (f"{X}.{mm.group(2)}" if mm.group(2) in local else mm.group(2)),
                   ctext, count=1)
    ctext = re.sub(r"(:\s*)(\w+)\b",
                   lambda mm: mm.group(1) + (f"{X}.{mm.group(2)}" if mm.group(2) in local else mm.group(2)),
                   ctext)
    m.edit(cmd, "")
    atext = m.text(alt)
    body = atext[atext.index("{") + 1:atext.index("}")]
    kept = [t for t in re.split(r"\s+or\s+", body.strip())
            if t.split(".")[-1] != cmd["id"]]
    if len(kept) == 1:
        # one of { A } is deprecated; a type naming one message is an alias
        lo = alt["span"]["start"]["offset"] + atext.index(" is ") + 4
        m.edits[alt["file"]].append((lo, alt["span"]["start"]["offset"] + atext.index("}") + 1,
                                     kept[0]))
    else:
        m.edits[alt["file"]].append((alt["span"]["start"]["offset"] + atext.index("{") + 1,
                                     alt["span"]["start"]["offset"] + atext.index("}"),
                                     "\n    " + " or ".join(kept) + "\n  "))
    ctx_text = m.text(ctx)
    at = ctx["span"]["start"]["offset"] + ctx_text.index("{") + 1
    m.edits[ctx["file"]].append((at, at, "\n" + ctext.strip() + "\n"
        f"type {req} is one of {{\n  {Ctx}.{cmd['id']} or {X}.{alt['id']}\n}} with {{\n"
        f"  briefly \"{X} requests\"\n  described as {{\n"
        f"    |What may be asked of {Ctx} about a {X}: {cmd['id']}, which the\n"
        f"    |context does itself by creating one, or any command for an existing one.\n"
        f"  }}\n}}\n"))
    # ports
    feeds_entity = set()
    for c in [n for n in m.nodes if n["kind"] == "connector"]:
        if under(c["to"].get("resolved", ""), ep):
            feeds_entity.add(c["from"].get("resolved"))
    for p in [n for n in m.nodes if n["kind"] in ("inlet", "outlet")]:
        t = p.get("type") if isinstance(p.get("type"), dict) else {}
        if t.get("resolved") != alt["path"] or under(p["path"], ep) \
                or p["path"] in feeds_entity:
            continue
        ptext = m.text(p)
        ref = t["ref"]
        i = ptext.index(" is ") + 4
        i = ptext.index(ref, i)
        start = p["span"]["start"]["offset"] + i
        m.edits[p["file"]].append((start, start + len(ref), f"{Ctx}.{req}"))
    m.renames.append((rf"\b(?:{Ctx}\.)?{X}\.{cmd['id']}\b", f"{Ctx}.{cmd['id']}"))
    if cmd_id:
        m.drops.append((f"{Ctx}.{cmd['id']}(", cmd_id[0]))


def drop_arg(text, head, field):
    """Remove 'field = value' from every constructor 'head(...)' in text."""
    out, i = "", 0
    while True:
        j = text.find(head, i)
        if j < 0:
            return out + text[i:]
        k = j + len(head)
        inner = ctor_args(text[j:])
        end = k + len(inner)
        args = split_args(inner)
        if field in args:
            del args[field]
            inner = ", ".join(f"{a} = {v}" for a, v in args.items())
        out += text[i:k] + inner
        i = end


def apply_edits(m):
    for f, es in m.edits.items():
        s = (m.dir / f).read_text()
        es = sorted(es, key=lambda e: (e[0], e[1]))
        for a, b in zip(es, es[1:]):
            if a[1] > b[0] and not (a[0] == a[1] or b[0] == b[1]):
                raise Skip(f"overlapping edits in {f}")
        for start, end, new in sorted(es, key=lambda e: (e[0], e[1]), reverse=True):
            s = s[:start] + new + s[end:]
        # a state whose only handler went is left 'is { }'
        s = re.sub(r"(state \w+ of record [\w.]+) is \{\s*\}", r"\1", s)
        (m.dir / f).write_text(s)
    for f in m.dir.rglob("*.riddl"):
        s = f.read_text()
        t = s
        for pat, rep in m.renames:
            t = re.sub(pat, rep, t)
        for head, field in m.drops:
            t = drop_arg(t, head, field)
        if t != s:
            f.write_text(t)


def main():
    argv = sys.argv[1:]
    apply = "--apply" in argv
    dirs = [ROOT / a for a in argv if not a.startswith("--")] or list(models())
    done = skipped = 0
    for d in dirs:
        m = Model(d)
        ents = [n for n in m.nodes if n["kind"] == "entity"]
        notes = []
        for e in ents:
            before = {f: list(v) for f, v in m.edits.items()}
            before_renames = list(m.renames)
            before_drops = list(m.drops)
            try:
                r = migrate_entity(m, e)
                if r:
                    notes.append("  ok    " + r)
                    done += 1
            except Skip as x:
                m.edits = defaultdict(list, before)
                m.renames = before_renames
                m.drops = before_drops
                if any(n["kind"] == "state" and n["parent"] == e["path"] for n in m.nodes):
                    notes.append(f"  SKIP  {e['id']}: {x}")
                    skipped += 1
        print(d.relative_to(ROOT))
        print("\n".join(notes))
        if apply and m.edits:
            try:
                apply_edits(m)
            except Skip as x:
                print(f"  NOT APPLIED: {x}")
        sys.stdout.flush()
    print(f"# {done} migrated, {skipped} skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
