#!/usr/bin/env python3
"""Digest for choosing a source event: the external commands to be driven,
and every internal event that could drive them, with briefs."""
import os
import json, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
# a relative RIDDLC is resolved against the repo root, since these
# scripts change directory per model (same rule as collect-warnings.py)
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = _r if os.path.isabs(_r) else str((ROOT / _r).resolve())

def nodes(n):
    if isinstance(n, dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)

def load(model):
    d = ROOT / model
    for c in d.glob("*.conf"):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        e = d / (m.group(1) if m else f"{d.name}.riddl")
    p = subprocess.run([RIDDLC, "dump", e.name, "--json"], cwd=d, capture_output=True, text=True)
    return list(nodes(json.loads(p.stdout)))

model, ctx, cmds = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
ns = load(model)
ext = next(c for c in ns if c.get("kind") == "context" and c.get("id") == ctx and c.get("intention") == "External")
print(f"### {model} -> {ctx}   [{ext['file']}:{ext['span']['start']['line']}]")
src = (ROOT / model / ext["file"]).read_text().splitlines()
print("   decl:", src[ext["span"]["start"]["line"]-1].strip()[:110])
print("   external context already has:",
      [f"{p['kind']} {p['id']}" for p in ns if p.get("kind") in ("inlet","outlet") and p.get("parent")==ext["path"]] or "no ports")
print("\n  commands to drive:")
for c in ns:
    if c.get("kind")=="command" and c.get("parent")==ext["path"]:
        mark = "*" if c["id"] in cmds else " "
        print(f"   {mark} {c['id']}: {c.get('brief')}")
print("\n  internal events:")
for e in ns:
    if e.get("kind")=="event" and not any(x.get("kind")=="context" and x.get("intention")=="External" and e["path"].startswith(x["path"]+".") for x in ns):
        print(f"     {e['path'].split('.',1)[1]}: {e.get('brief')}")
