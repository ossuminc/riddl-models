#!/usr/bin/env python3
"""Classify every msg-answer-unreachable site by the route its answer can take.

Input: a collect-warnings.py JSONL file. For each finding, from the model's
`riddlc dump --json`:

  sender     the processor that sends the command (ancestor of the statement)
  answerer   the entity that declares the answering event
  route      the streamlet fed by the answerer's outlet that admits the event
             (its "event split"), when one exists in the sender's context

Prints one JSON record per finding with a `case`:

  split-local   the answerer's event split is in the sender's context:
                add an outlet there, an inlet on the sender, a connector
  no-split      the answerer publishes the event but no streamlet is fed by it
  cross-context the answerer lives in another context than the sender
  unparsed      the message did not match

Usage: RIDDLC=... ./scripts/answers/facts.py <warnings.jsonl> > facts.jsonl
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

MSG = re.compile(
    r"(\w+) '(\w+)' (?:sends|tells) (\w+) '(\w+)', which is answered with "
    r"(\w+) '(\w+)', but the answer cannot reach \w+ '\w+': (.*)")

# `riddlc dump` names a streamlet by its SHAPE, never "streamlet"
STREAMLET_KINDS = {"source", "sink", "flow", "split", "merge", "router",
                   "void", "streamlet"}


def dump(model):
    d = ROOT / model
    entry = next(d.glob("*.conf")).stem + ".riddl"
    out = subprocess.run([RIDDLC, "dump", entry, "--json"], cwd=d,
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    finds = [json.loads(l) for l in open(sys.argv[1]) if l.startswith("{")]
    finds = [f for f in finds if f["rule"] == "msg-answer-unreachable"]
    by_model = defaultdict(list)
    for f in finds:
        by_model[f["model"]].append(f)
    for model, fs in sorted(by_model.items()):
        nodes = dump(model)
        by_path = {n["path"]: n for n in nodes if "path" in n}
        # statements at a (file, line, col)
        at = {}
        for n in nodes:
            s = n.get("span", {}).get("start", {})
            if "line" in s:
                at.setdefault((n.get("file"), s["line"], s.get("col")), n)
        conns = [n for n in nodes if n.get("kind") == "connector"]
        feeds = {c["from"]["resolved"]: c["to"]["resolved"] for c in conns
                 if c.get("from", {}).get("resolved")}
        for f in fs:
            m = MSG.match(f["message"])
            rec = {"model": model, "file": f["file"], "line": f["line"]}
            if not m:
                rec["case"] = "unparsed"
                print(json.dumps(rec)); continue
            skind, sname, _, cmd, _, evt, why = m.groups()
            rec.update(senderKind=skind, sender=sname, command=cmd,
                       event=evt, why=why[:100])
            stmt = at.get((f["file"], f["line"], f["col"]))
            anc = stmt.get("ancestors", []) if stmt else []
            sender = next((a for a in reversed(anc)
                           if a.split(".")[-1] == sname), None)
            rec["senderPath"] = sender
            ev = [n for n in nodes if n.get("kind") == "event"
                  and n.get("id") == evt]
            ents = [by_path.get(n["parent"]) for n in ev]
            ents = [e for e in ents if e and e.get("kind") == "entity"]
            if len(ents) != 1:
                rec["case"] = f"answerer-{len(ents)}"
                print(json.dumps(rec)); continue
            ent = ents[0]
            rec["answerer"] = ent["path"]
            sctx = next((a for a in reversed(anc)
                         if by_path.get(a, {}).get("kind") == "context"), None)
            ectx = ent["parent"]
            rec["senderContext"], rec["answererContext"] = sctx, ectx
            if sctx != ectx and sender != ectx:
                rec["case"] = "cross-context"
                print(json.dumps(rec)); continue
            outs = [n for n in nodes if n.get("kind") == "outlet"
                    and n.get("parent") == ent["path"]]
            dests = [feeds.get(o["path"]) for o in outs]
            splits = [d.rsplit(".", 1)[0] for d in dests if d]
            splits = [s for s in splits
                      if by_path.get(s, {}).get("kind") in STREAMLET_KINDS]
            rec["splits"] = splits
            rec["case"] = "split-local" if len(splits) == 1 else \
                ("no-split" if not splits else "many-splits")
            print(json.dumps(rec))


if __name__ == "__main__":
    main()
