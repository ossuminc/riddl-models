#!/usr/bin/env python3
"""Digest inbound placeholder sites for placement decisions.

Per model: each pending event, the command/query of ours that causes it (so the
emission has somewhere to hang), and OUR local commands -- which is what the
counterparty test is applied against.
"""
import json, re, subprocess, collections, sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
def entry(d):
    c=list(d.glob("*.conf"))[0]
    m=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text())
    return d/(m.group(1) if m else f"{d.name}.riddl")
lo,hi=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (0,10**9)
models=sorted({str(p.parent.relative_to(ROOT)) for p in ROOT.glob("*/*/*/*.riddl")
               if 'the model receives' in p.read_text()})
for idx,model in enumerate(models):
    if not (lo<=idx<hi): continue
    d=ROOT/model; e=entry(d)
    ns=list(nodes(json.loads(subprocess.run([R,"dump",e.name,"--json"],cwd=d,
                                            capture_output=True,text=True).stdout)))
    exts={n["path"]:n["id"] for n in ns if n.get("kind")=="context" and n.get("intention")=="External"}
    allsrc="".join((d/f.name).read_text() for f in d.glob("*.riddl"))
    driven=set(re.findall(r"\b(?:tell|send)\s+(?:command\s+)?([\w.]+)", allsrc))
    driven|={x.split(".")[-1] for x in re.findall(r"let \w+: type ([\w.]+) = prompt", allsrc)}
    asked={x.split(".")[-1] for x in re.findall(r"ask query ([\w.]+) of", allsrc)}
    # a repository's own Persist<Event> commands are never what an external
    # event should drive, so they are noise in this decision
    ours=sorted({f'{n["parent"].split(".")[-1]}.{n["id"]}' for n in ns
                 if n.get("kind")=="command" and n.get("parent") not in exts
                 and not n["id"].startswith("Persist")})
    print(f"\n### {model}   [{idx}]")
    print(f"    our commands: {', '.join(ours)}")
    pend=collections.defaultdict(list)
    for a in [n for n in ns if n.get("kind")=="adaptor"]:
        txt=(d/a["file"]).read_text()
        body=txt[a["span"]["start"]["offset"]:a["span"]["end"]["offset"]]
        hm=re.match(r"adaptor\s+(\w+)\s+from\s+context\s+([\w.]+)", body)
        if not hm: continue
        ctx=hm.group(2).split(".")[-1]
        cp=next((p for p,i in exts.items() if i==ctx), None)
        for cm in re.finditer(r'^\s*on event ([\w.]+) is \{\n\s*do "the model receives[^"]*"\n', body, re.M):
            pend[ctx].append(cm.group(1).split(".")[-1])
        if ctx in pend:
            cmds=sorted({n["id"] for n in ns if n.get("kind")=="command" and n.get("parent")==cp})
            qs=sorted({n["id"] for n in ns if n.get("kind")=="query" and n.get("parent")==cp})
            dc=[c for c in cmds if c in driven]; dq=[q for q in qs if q in asked]
            print(f"    {ctx}: {', '.join(pend[ctx])}")
            print(f"        we send: {dc or '-'}   we ask: {dq or '-'}")
