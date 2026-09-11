#!/usr/bin/env python3
"""Insert the corpus-standard `<Entity>EventSplit` between an entity and the one
consumer its outlet feeds directly, so drain-inlets.py can hang adaptor legs
off it.   Usage: insert-split.py <model-dir> <Entity>"""
import json,re,subprocess,sys
from pathlib import Path
R="/Users/reid/Code/ossuminc/bin/riddlc"; d=Path(sys.argv[1]); ent=sys.argv[2]
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
c=next(d.glob("*.conf")); e=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()).group(1)
ns=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout))); byp={n["path"]:n for n in ns if "path" in n}
E=next(n for n in ns if n.get("kind")=="entity" and n["id"]==ent); ctx=byp[E["parent"]]
O=[p for p in ns if p.get("kind")=="outlet" and p.get("parent")==E["path"]]; assert len(O)==1; O=O[0]
C=[c for c in ns if c.get("kind")=="connector" and (c.get("from") or {}).get("resolved")==O["path"]]; assert len(C)==1; C=C[0]
T=byp[C["to"]["resolved"]]; TP=byp[T["parent"]]
ty=byp[O["type"]["resolved"]]; tsrc=(d/ty["file"]).read_text()[ty["span"]["start"]["offset"]:ty["span"]["end"]["offset"]]
members=[m for m in re.findall(r"[\w.]+", tsrc.split("{",1)[1].split("}",1)[0]) if m!="or"]
tyref=O["type"]["ref"]; S=f"{ent}EventSplit"; out=f"{S}To{TP['id']}"
clauses=""
for m in members:
    en=m.split(".")[-1]; b=en[0].lower()+en[1:]
    clauses+=f"    on {b}: event {ent}.{en} is {{\n      send {b} to outlet {out}\n    }}\n"
split=f'''  streamlet {S} as flow is {{
    inlet {S}In is type {tyref}
    outlet {out} is type {tyref}
    handler {S}Handler is {{
{clauses}      on other is {{
        error "Unexpected message for split {S}"
      }}
    }} with {{
      briefly "{ent} event fan-out"
    }}
  }} with {{
    briefly "{ent} events, fanned out to their consumers"
    described as {{
      |Every event {ent} emits passes through here on its way to the read model
      |and to the adaptors that translate it for other contexts.
    }}
  }}
'''
# place the split right before the connector; repoint the connector; add the feed
f=C["file"]; t=(d/f).read_text(); cs,ce=C["span"]["start"]["offset"],C["span"]["end"]["offset"]
seg=t[cs:ce]; old=C["from"]["ref"]; seg2=re.sub(rf"from outlet {re.escape(old)}(?![\w.])", f"from outlet {ctx['id']}.{S}.{out}", seg, count=1); assert seg2!=seg
ls=t.rfind("\n",0,cs)+1
feed=f"  connector '{ent}Event Stream' is from outlet {ctx['id']}.{ent}.{O['id']} to inlet {ctx['id']}.{S}.{S}In with {{\n    briefly \"Every {ent} event, on its way to the fan-out\"\n  }}\n"
t=t[:ls]+split+feed+t[ls:cs]+seg2+t[ce:]
(d/f).write_text(t)
p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True)
errs=[l for l in (p.stdout+p.stderr).splitlines() if l.strip().startswith("[error]")]
print(f"{d.name}/{ent}: split inserted before {TP['id']}; {len(errs)} errors"); [print("  ",l[:160]) for l in errs[:4]]
