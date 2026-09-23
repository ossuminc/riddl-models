#!/usr/bin/env python3
"""Census for riddl-generator's TicketDisplaySink finding: a connector that
delivers an entity an event the entity itself yields. Nothing outside an
entity should hand it back its own event -- it produced it and folded it from
its journal."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R=sys.argv[1] if len(sys.argv)>1 else "/Users/reid/Code/ossuminc/bin/riddlc"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
def entry(d):
    for c in d.glob("*.conf"):
        m=re.search(r'input-file\s*=\s*"([^"]+)"',c.read_text())
        if m: return m.group(1)
hits=0; swept=0
models=[ROOT/a for a in sys.argv[2:]] if len(sys.argv)>2 else sorted({c.parent for c in ROOT.rglob("*.conf") if "patterns" not in c.parts and "/1/" not in str(c)})
for d in models:
    e=entry(d)
    if not e: continue
    p=subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True)
    try: ns=list(nodes(json.loads(p.stdout)))
    except Exception: print(f"# {d}: dump failed",file=sys.stderr); continue
    swept+=1
    byp={n["path"]:n for n in ns if "path" in n}
    # every event an entity yields, by path
    yielded={}
    for n in ns:
        if n["kind"]=="event":
            par=byp.get(n["parent"],{})
            if par.get("kind")=="entity": yielded[n["path"]]=par["path"]
    for c in ns:
        if c["kind"]!="connector": continue
        to=c.get("to",{}).get("resolved")
        inlet=byp.get(to or "")
        if not inlet or inlet["kind"]!="inlet": continue
        owner=byp.get(inlet["parent"],{})
        if owner.get("kind")!="entity": continue
        ty=inlet.get("type",{}) if isinstance(inlet.get("type"),dict) else {}
        members=[m["resolved"] for m in (ty.get("alternation") or [])] or ([ty["resolved"]] if ty.get("resolved") else [])
        own=[m for m in members if yielded.get(m)==owner["path"]]
        if own:
            hits+=1
            print(f"{d.relative_to(ROOT)}: connector {c['id']!r} -> {owner['id']}.{inlet['id']} carries its own {', '.join(m.split('.')[-1] for m in own)}")
print(f"{hits} connectors deliver an entity its own event, across {swept} models")
