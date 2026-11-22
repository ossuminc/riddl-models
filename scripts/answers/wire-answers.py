#!/usr/bin/env python3
"""Wire each unreachable command answer back to its sender (Reid, 2026-11-21).

riddl 2.8.2-4 (`msg-answer-unreachable`): a command that `yields` an event is
answered on the yielder's outlets; there is no unwired return channel, so a
sender with no inlet admitting the answer loses it. Reid ruled (a): every
answer is wired home, and the sender receives it, even if only to `log` it.

Input: facts.jsonl from `facts.py`. Only `split-local` sites are handled: the
answering entity already publishes into an event split in the sender's
context. Per (sender, split) route:

  split    gains   outlet <Split>To<Sender> is event E | type <SplitInletType>
           and its clause for each answer event gains `send b to outlet ...`
  sender   gains   inlet <Entity>Answers of the same type, its shape follows
           its new arity, and a clause `on b: event Ent.E is { log b }`
           before its `on other`
  context  gains   connector '<Sender> <Entity> Answers'

A route whose connector already exists only gains the sends and clauses.
Anything the script cannot place exactly is reported and left alone.

Usage: RIDDLC=... ./scripts/answers/wire-answers.py facts.jsonl [--apply]
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
RIDDLC = _r if os.path.isabs(_r) else str((ROOT / _r).resolve())
STREAMLET_KINDS = {"source", "sink", "flow", "split", "merge", "router",
                   "void", "streamlet"}


def shape_for(outlets, inlets):
    if outlets == 0 and inlets == 0: return "void"
    if inlets == 0: return "source"
    if outlets == 0: return "sink"
    if outlets == 1 and inlets == 1: return "flow"
    if inlets == 1: return "split"
    if outlets == 1: return "merge"
    return "router"


def dump(model):
    d = ROOT / model
    entry = next(d.glob("*.conf")).stem + ".riddl"
    out = subprocess.run([RIDDLC, "dump", entry, "--json"], cwd=d,
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def last(p): return p.rsplit(".", 1)[-1]


def lc(s): return s[0].lower() + s[1:]


class Edits:
    """Line-anchored edits per file: inserts before a 1-based line, and
    in-line substitutions checked against the expected old text."""
    def __init__(self):
        self.ins = defaultdict(lambda: defaultdict(list))
        self.sub = defaultdict(dict)

    def before(self, f, line, text): self.ins[f][line].append(text)
    def after(self, f, line, text): self.ins[f][line + 1].append(text)
    def shape(self, f, line, old, new): self.sub[f][line] = (old, new)

    def apply(self, root):
        for f in set(self.ins) | set(self.sub):
            p = root / f
            L = p.read_text().split("\n")
            for line, (old, new) in self.sub[f].items():
                s = L[line - 1]
                pat = re.compile(r"\bas " + old + r"\b")
                if not pat.search(s):
                    raise SystemExit(f"{f}:{line}: no 'as {old}' in: {s}")
                L[line - 1] = pat.sub("as " + new, s, count=1)
            for line in sorted(self.ins[f], reverse=True):
                L[line - 1:line - 1] = self.ins[f][line]
            p.write_text("\n".join(L))


def main():
    facts = [json.loads(l) for l in open(sys.argv[1])]
    apply = "--apply" in sys.argv
    skipped = [f for f in facts if f["case"] != "split-local"]
    routes = defaultdict(list)
    for f in facts:
        if f["case"] == "split-local":
            routes[(f["model"], f["senderPath"], f["splits"][0],
                    f["answerer"])].append(f)
    by_model = defaultdict(dict)
    for k, v in routes.items():
        by_model[k[0]][k] = v
    refused, done = [], 0
    for model, rts in sorted(by_model.items()):
        nodes = dump(model)
        P = {n["path"]: n for n in nodes if "path" in n}
        kids = defaultdict(list)
        for n in nodes:
            if "parent" in n: kids[n["parent"]].append(n)
        conns = [n for n in nodes if n.get("kind") == "connector"]
        ed = Edits()
        # arity deltas accumulate across routes touching the same processor
        d_in, d_out = defaultdict(int), defaultdict(int)
        shape_site = {}
        for (m, sp, xp, ep), fs in sorted(rts.items()):
            sender, split, ent = P[sp], P[xp], P[ep]
            red, bad = Edits(), False          # this route's edits, all or nothing
            r_out = r_in = 0; r_shapes = {}
            if sp == xp:
                refused.append((model, sp, "sender is the split itself")); continue
            ctx = split["parent"]
            ctx_id = last(ctx)
            events = []
            for f in fs:
                ev = next((n for n in kids[ep] if n.get("kind") == "event"
                           and n["id"] == f["event"]), None)
                if ev and ev["path"] not in [e["path"] for e in events]:
                    events.append(ev)
            xin = [n for n in kids[xp] if n.get("kind") == "inlet"]
            if len(xin) != 1:
                refused.append((model, xp, "split has %d inlets" % len(xin))); continue
            alt = {a["resolved"] for a in xin[0].get("type", {}).get("alternation", [])}
            if len(events) == 1:
                typ = f"event {last(ep)}.{events[0]['id']}"
            elif all(e["path"] in alt for e in events):
                typ = f"type {xin[0]['type']['ref']}"
            else:
                refused.append((model, sp, "answers not in split inlet type")); continue
            # an existing connector from this split into this sender?
            s_inlets = {n["path"] for n in kids[sp] if n.get("kind") == "inlet"}
            x_outlets = {n["path"]: n for n in kids[xp] if n.get("kind") == "outlet"}
            existing = [c for c in conns if c["from"].get("resolved") in x_outlets
                        and c["to"].get("resolved") in s_inlets]
            if existing:
                out_name = last(existing[0]["from"]["resolved"])
                oalt = {a["resolved"] for a in x_outlets[existing[0]["from"]["resolved"]]
                        .get("type", {}).get("alternation", [])}
                oref = x_outlets[existing[0]["from"]["resolved"]].get("type", {}).get("resolved")
                if not all(e["path"] in oalt or e["path"] == oref for e in events):
                    refused.append((model, sp, "existing route does not admit answers")); continue
            else:
                out_name = f"{last(xp)}To{last(sp)}"
                in_name = f"{last(ep)}Answers"
                taken = {n["id"] for n in kids[xp] + kids[sp]
                         if n.get("kind") in ("inlet", "outlet")}
                if out_name in taken or in_name in taken:
                    refused.append((model, sp, f"name taken: {out_name}/{in_name}")); continue
                xs, ss = split["span"]["start"], sender["span"]["start"]
                ind_x = " " * (xs["col"] + 1)
                ind_s = " " * (ss["col"] + 1)
                red.after(split["file"], xs["line"], f"{ind_x}outlet {out_name} is {typ}")
                red.after(sender["file"], ss["line"], f"{ind_s}inlet {in_name} is {typ}")
                s_ref = ctx_id if sp == ctx else f"{ctx_id}.{last(sp)}"
                cname = f"{last(sp)} {last(ep)} Answers"
                if any(c["id"] == cname for c in conns):
                    refused.append((model, sp, f"connector name taken: {cname}")); continue
                red.before(split["file"], xs["line"],
                          " " * (xs["col"] - 1) +
                          f"connector '{cname}' is from outlet {ctx_id}.{last(xp)}.{out_name} "
                          f"to inlet {s_ref}.{in_name}")
                r_out, r_in = 1, 1
                r_shapes = {xp: split, sp: sender}
            # split: a send in each answer event's clause
            xh = [n for n in kids[xp] if n.get("kind") == "handler"]
            xclauses = [c for h in xh for c in kids[h["path"]] if c.get("kind") == "on-event"]
            for e in events:
                cl = next((c for c in xclauses
                           if c.get("message", {}).get("resolved") == e["path"]), None)
                if not cl or not cl.get("binding"):
                    refused.append((model, xp, f"no bound clause for {e['id']}")); bad = True; break
                cs = cl["span"]["start"]
                red.after(cl["file"], cs["line"],
                         " " * (cs["col"] + 1) + f"send {cl['binding']} to outlet {out_name}")
            # sender: a clause that receives each answer
            sh = [n for n in kids[sp] if n.get("kind") == "handler"]
            sclauses = [c for h in sh for c in kids[h["path"]] if c.get("kind") == "on-event"]
            others = [c for h in sh for c in kids[h["path"]] if c.get("kind") == "on-other"]
            for e in events:
                if any(c.get("message", {}).get("resolved") == e["path"] for c in sclauses):
                    continue
                if not others:
                    refused.append((model, sp, f"no 'on other' to place {e['id']}")); bad = True; break
                o = others[0]; os_ = o["span"]["start"]; ind = " " * (os_["col"] - 1)
                b = lc(e["id"])
                red.before(o["file"], os_["line"],
                          f"{ind}on {b}: event {last(ep)}.{e['id']} is {{\n"
                          f"{ind}  log {b}\n{ind}}}")
            if bad:
                continue
            for f_, lines in red.ins.items():
                for ln, txts in lines.items():
                    ed.ins[f_][ln].extend(txts)
            d_out[xp] += r_out; d_in[sp] += r_in
            shape_site.update(r_shapes)
            done += len(fs)
        for p, node in shape_site.items():
            a = node["arity"]
            new = shape_for(a["outlets"] + d_out[p], a["inlets"] + d_in[p])
            old = node.get("ascribedShape")
            if old and old != new:
                ed.shape(node["file"], node["span"]["start"]["line"], old, new)
        if apply:
            ed.apply(ROOT / model)
    print(f"sites wired: {done}; skipped (not split-local): {len(skipped)}; "
          f"refused routes: {len(refused)}", file=sys.stderr)
    for r in refused:
        print("REFUSED", *r, file=sys.stderr)


if __name__ == "__main__":
    main()
