#!/usr/bin/env python3
"""Census: external-context commands that no handler clause handles.

riddlc has no rule for this (filed 2026-09-11 as
../riddl/task/2026-09-11-external-context-unhandled-command.md): a message an
external context's inlet admits, that is actually sent, and that only `on other`
can catch, validates at zero. This sweeps every external context and prints
each declared command with no `on command` clause under that context.

Prints the denominator on stderr. A "0 unhandled" from a run that swept 0
contexts is worth nothing; check the denominator against 189 / 782.
"""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
tot=ctxs=gaps=0
for c in sorted(ROOT.glob("*/*/*/*.conf")):
    d=c.parent; m=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()); e=m.group(1)
    p=subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True)
    if not p.stdout.strip(): continue
    ns=list(nodes(json.loads(p.stdout))); tot+=1
    for x in ns:
        if x.get("kind")=="context" and x.get("intention")=="External":
            ctxs+=1
            cmds={n["id"] for n in ns if n.get("kind")=="command" and n.get("parent")==x["path"]}
            handled={(n.get("message") or {}).get("resolved","").split(".")[-1] for n in ns if n.get("kind")=="onmessageclause" and n.get("path","").startswith(x["path"]+".")}
            for miss in sorted(cmds-handled):
                gaps+=1; print(f"{d.relative_to(ROOT)}  {x['id']}.{miss}")
print(f"models {tot}, external contexts {ctxs}, unhandled commands {gaps}", file=sys.stderr)
