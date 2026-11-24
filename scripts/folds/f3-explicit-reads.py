#!/usr/bin/env python3
"""Tighten scripts/folds/f3-placement.tsv with what each clause already
says: a clause (or, in an event-sourced entity, the command that yields its
event) that reads `<Entity>.<State>.` or `<StateRecord>.` was written for
that state, so that state is its source. The target state is ignored (a
fold may set fields of the state it enters).

Rows whose sources change get basis `explicit-read`. Prints a summary.
Run with python3 -P (scripts/folds/collections.py shadows the stdlib).
"""
import csv, collections, json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TSV = ROOT / "scripts/folds/f3-placement.tsv"
RIDDLC = os.environ.get("RIDDLC", "riddlc")
IF = re.compile(r'^\s*input-file\s*=\s*"?([^"\s]+)"?', re.M)

rows = list(csv.DictReader(TSV.open(), delimiter="\t"))
changed = collections.Counter()
for model in dict.fromkeys(r["model"] for r in rows):
    conf = next((ROOT / model).glob("*.conf"))
    m = IF.search(conf.read_text())
    e = m.group(1) if m else conf.stem + ".riddl"
    d = json.loads(subprocess.run([RIDDLC, "dump", e, "--json"], cwd=ROOT / model,
                                  capture_output=True, text=True).stdout)
    by = {x["path"]: x for x in d if "path" in x}
    kids = collections.defaultdict(list)
    for x in d:
        if "parent" in x: kids[x["parent"]].append(x)
    def text(n):
        s = (ROOT / model / n["file"]).read_text()
        return s[n["span"]["start"]["offset"]:n["span"]["end"]["offset"]]
    for r in rows:
        if r["model"] != model or r["clause"] not in by: continue
        ent = by[r["entity"]]; eid = ent["id"]
        states = {x["id"]: x for x in kids[r["entity"]] if x.get("kind") == "state"}
        recs = {}
        for sid, st in states.items():
            mm = re.search(r"of\s+record\s+([\w.]+)", text(st))
            recs[mm.group(1).split(".")[-1]] = sid
        c = by[r["clause"]]
        bodies = [text(c)]
        if c["kind"] == "on-event":
            ev = c["message"]["resolved"].split(".")[-1]
            for k in kids[c["parent"]]:
                if k.get("kind") == "onmessageclause":
                    t = text(k)
                    if re.search(r"\byield\s+event\s+(?:[\w.]+\.)?" + ev + r"\b", t):
                        bodies.append(t)
        reads = set()
        for b in bodies:
            b = re.sub(r'"(?:[^"\\]|\\.)*"', '""', b)
            for sid in states:
                if re.search(r"\b" + eid + r"\." + sid + r"\.", b): reads.add(sid)
            for rid, sid in recs.items():
                if re.search(r"(?<![\w.])" + rid + r"\.", b): reads.add(sid)
        reads.discard(r["target"])
        if reads and set(r["sources"].split(",")) != reads:
            r["sources"] = ",".join(s for s in states if s in reads)
            r["basis"] = "explicit-read"; changed[model] += 1

with TSV.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
print(sum(changed.values()), "rows tightened in", len(changed), "models")
for m, n in changed.items(): print(" ", m, n)
