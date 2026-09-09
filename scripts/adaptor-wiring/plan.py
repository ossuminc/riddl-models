#!/usr/bin/env python3
"""For each census pair, say whether an OUTBOUND adaptor to that external
context exists and what state it is in.  Three outcomes:
  SETUP   -- adaptor exists but is a port-less placeholder
  INSERT  -- adaptor exists and is already wired (has an outlet)
  BUILD   -- no outbound adaptor to that context at all
"""
import os
import json, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
# a relative RIDDLC is resolved against the repo root, since these
# scripts change directory per model (same rule as collect-warnings.py)
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = _r if os.path.isabs(_r) else str((ROOT / _r).resolve())

def entry(d):
    for c in d.glob("*.conf"):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        return d / (m.group(1) if m else f"{d.name}.riddl")

def nodes(n):
    if isinstance(n, dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)

TO = re.compile(r'adaptor\s+(\w+)\s+to\s+context\s+([\w.]+)')

cache = {}
def model_nodes(model):
    if model not in cache:
        d = ROOT / model; e = entry(d)
        p = subprocess.run([RIDDLC, "dump", e.name, "--json"], cwd=d,
                           capture_output=True, text=True)
        cache[model] = list(nodes(json.loads(p.stdout)))
    return cache[model]

rows = [json.loads(l) for l in open(sys.argv[1])]
pairs = {}
for r in rows:
    pairs.setdefault((r["model"], r["ctx"]), []).append(r["id"])

for (model, ctx), cmds in sorted(pairs.items()):
    ns = model_nodes(model)
    hit = None
    for a in ns:
        if a.get("kind") != "adaptor": continue
        src = (ROOT / model / a["file"]).read_text().splitlines()
        line = src[a["span"]["start"]["line"] - 1]
        m = TO.search(line[a["span"]["start"]["col"] - 1:])
        if m and m.group(2).split(".")[-1] == ctx:
            hit = (a, m.group(1)); break
    if not hit:
        print(f"BUILD   {model} [{ctx}] {','.join(cmds)}")
        continue
    a, name = hit
    outs = [p for p in ns if p.get("kind") == "outlet" and p.get("parent") == a["path"]]
    kind = "INSERT" if outs else "SETUP"
    print(f"{kind:7s} {model} [{ctx}] {','.join(cmds)}  adaptor={name} @{a['file']}:{a['span']['start']['line']} outlets={[o['id'] for o in outs]}")
