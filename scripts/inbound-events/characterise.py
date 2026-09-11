#!/usr/bin/env python3
"""Characterise every REMAINING inbound placeholder, so decisions can be taken
per CLASS rather than per site."""
import json, re, subprocess, collections
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
SP=Path("scripts/inbound-events")
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
rows=[]
for p in sorted(ROOT.glob("*/*/*/*.riddl")):
    if 'the model receives' not in p.read_text(): continue
    d=p.parent
    if any(r["model"]==str(d.relative_to(ROOT)) for r in rows): continue
    c=list(d.glob("*.conf"))[0]
    m=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text())
    e=d/(m.group(1) if m else f"{d.name}.riddl")
    ns=list(nodes(json.loads(subprocess.run([R,"dump",e.name,"--json"],cwd=d,
                                            capture_output=True,text=True).stdout)))
    exts={n["path"]:n["id"] for n in ns if n.get("kind")=="context" and n.get("intention")=="External"}
    allsrc="".join((d/f.name).read_text() for f in d.glob("*.riddl"))
    driven={x.split(".")[-1] for x in re.findall(r"\b(?:tell|send)\s+(?:command\s+)?([\w.]+)", allsrc)}
    driven|={x.split(".")[-1] for x in re.findall(r"let \w+: type ([\w.]+) = prompt", allsrc)}
    asked={x.split(".")[-1] for x in re.findall(r"ask query ([\w.]+) of", allsrc)}
    for a in [n for n in ns if n.get("kind")=="adaptor"]:
        txt=(d/a["file"]).read_text()
        body=txt[a["span"]["start"]["offset"]:a["span"]["end"]["offset"]]
        hm=re.match(r"adaptor\s+\w+\s+from\s+context\s+([\w.]+)", body)
        if not hm: continue
        ctx=hm.group(1).split(".")[-1]
        cp=next((k for k,v in exts.items() if v==ctx), None)
        cmds={n["id"] for n in ns if n.get("kind")=="command" and n.get("parent")==cp}
        qs={n["id"] for n in ns if n.get("kind")=="query" and n.get("parent")==cp}
        for cm in re.finditer(r'^\s*on event ([\w.]+) is \{\n\s*do "the model receives[^"]*"\n', body, re.M):
            ev=cm.group(1).split(".")[-1]
            rows.append(dict(model=str(d.relative_to(ROOT)), ctx=ctx, event=ev,
                             ack=bool(cmds & driven), asks=bool(qs & asked),
                             has_cmds=bool(cmds)))
json.dump(rows, open(SP/"remaining.json","w"), indent=1)
print(f"remaining sites: {len(rows)}  in {len({(r['model'],r['ctx']) for r in rows})} external contexts, "
      f"{len({r['model'] for r in rows})} models")
# morphology of the event name: the trailing past participle is the act
tail=collections.Counter()
for r in rows:
    w=re.findall(r"[A-Z][a-z]+|[A-Z]+(?![a-z])", r["event"])
    tail[w[-1] if w else r["event"]]+=1
print("\n=== trailing word of the event name (the ACT), top 40 ===")
for k,v in tail.most_common(40): print(f"{v:5d}  -{k}")
print(f"\ndistinct trailing words: {len(tail)}")
print("\n=== ownership ===")
print(collections.Counter((('ack' if r['ack'] else ('asked' if r['asks'] else 'events-only')))
                          for r in rows).most_common())
