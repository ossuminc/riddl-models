#!/usr/bin/env python3
"""Build a cross-context event stream (reactive-bbq, or any multi-context model):

  <Entity fan-out> --leg--> <S>.<S>To<T>In --boundary relay--> <S>.<S>To<T>Out
      --domain connector--> <T>.<Adaptor>.<Adaptor>In

Usage: cross-stream.py <model-dir> <SourceCtx> <Entity> <TargetCtx> <Adaptor> <Event,Event,...>
The fan-out is the streamlet in <SourceCtx> that already handles the entity's
events with >=2 outlets; the relay is the context's own boundary handler (a
send may only name an outlet the sender owns, and a streamlet does not own
its context's outlet -- the shape ShiftToReporting already uses).
"""
import json,re,subprocess,sys
from pathlib import Path
R="/Users/reid/Code/ossuminc/bin/riddlc"
d=Path(sys.argv[1]); S,E,T,A=sys.argv[2:6]; EVS=sys.argv[6].split(",")
MULTI=len(sys.argv)>7   # the adaptor takes streams from more than one entity: name the inlet per entity
INLET=f"{A}From{E}In" if MULTI else f"{A}In"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
c=next(d.glob("*.conf")); e=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()).group(1)
ns=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout))); byp={n["path"]:n for n in ns if "path" in n}
Sn=next(n for n in ns if n.get("kind")=="context" and n["id"]==S); Tn=next(n for n in ns if n.get("kind")=="context" and n["id"]==T)
En=next(n for n in ns if n.get("kind")=="entity" and n["id"]==E and n["parent"]==Sn["path"])
An=next(n for n in ns if n.get("kind")=="adaptor" and n["id"]==A and n["parent"]==Tn["path"])
evp={En["path"]+"."+x for x in EVS}
fan=[s for s in ns if s.get("kind") in ("split","router") and s.get("parent")==Sn["path"] and {(c.get("message") or {}).get("resolved") for c in ns if c.get("kind")=="on-event" and c.get("path","").startswith(s["path"]+".")} >= evp]
assert fan, "no fan-out covers "+str(EVS); F=fan[0]
O=[p for p in ns if p.get("kind")=="outlet" and p.get("parent")==En["path"]][0]; tyref=O["type"]["ref"]
files={}
def txt(f): return files.setdefault(f,(d/f).read_text())
edits=[]
leg=f"{F['id']}To{T}"; ft=txt(F["file"])
first=next(p for p in ns if p.get("kind") in ("inlet","outlet") and p.get("parent")==F["path"])
ind=re.match(r"[ \t]*",ft[ft.rfind("\n",0,first["span"]["start"]["offset"])+1:]).group(0)
edits.append((F["file"],first["span"]["start"]["offset"],f"outlet {leg} is type {tyref}\n{ind}"))
for cl in ns:
    if cl.get("kind")=="on-event" and cl.get("path","").startswith(F["path"]+".") and (cl.get("message") or {}).get("resolved") in evp:
        b=cl["binding"] if isinstance(cl.get("binding"),str) else cl["binding"]["id"]
        body=ft[cl["span"]["start"]["offset"]:cl["span"]["end"]["offset"]]
        lm=list(re.finditer(r"^(\s*)send \w+ to outlet [\w.]+\n", body, re.M))[-1]
        edits.append((F["file"],cl["span"]["start"]["offset"]+lm.end(),f"{lm.group(1)}send {b} to outlet {leg}\n"))
st=txt(Sn["file"]); ss=Sn["span"]["start"]["offset"]
hm=re.match(r"((?:\w+ )*context \w+)( as \w+)?( is \{[ \t]*\n)", st[ss:ss+200]); assert hm
H=[h for h in ns if h.get("kind")=="handler" and h.get("parent")==Sn["path"]]; assert H, "source context has no boundary handler"; H=H[0]
edits.append((Sn["file"],ss+hm.end(),f"  inlet {S}{E}To{T}In is type {tyref}  outlet {S}{E}To{T}Out is type {tyref}\n  connector '{A} {E} Feed' is from outlet {S}.{F['id']}.{leg} to inlet {S}.{S}{E}To{T}In with {{\n    briefly \"{E} events on their way to {T}\"\n  }}\n"))
relay="".join(f"    on {ev[0].lower()+ev[1:]}: event {E}.{ev} is {{\n      send {ev[0].lower()+ev[1:]} to outlet {S}.{S}{E}To{T}Out\n    }}\n" for ev in EVS)
hh=txt(H["file"]); hs=H["span"]["start"]["offset"]; hm2=re.match(r"\s*handler \w+ is \{[ \t]*\n", hh[hs:hs+120]); assert hm2
edits.append((H["file"],hs+hm2.end(),relay))
at_=txt(An["file"]); as_=An["span"]["start"]["offset"]; am=re.match(r"adaptor \w+ from context [\w.]+( as \w+)? is \{[ \t]*\n", at_[as_:as_+200]); assert am
aind=re.search(r"^(\s*)(inlet|outlet|handler) ", at_[as_+am.end():as_+am.end()+400], re.M).group(1)
edits.append((An["file"],as_+am.end(),f"{aind}inlet {INLET} is type {O['type']['resolved']}\n"))
et=txt(e); em=re.search(r"^(\s*)domain [\w.]+ is \{\n", et, re.M); di=em.group(1)+"  "
edits.append((e,em.end(),f"{di}persistent connector '{E}Event Stream To {T}' is from outlet {S}.{S}{E}To{T}Out to inlet {T}.{A}.{INLET} with {{\n{di}  briefly \"What {S} tells {T} about its {E.lower()}s\"\n{di}}}\n"))
for f,at,s in sorted(edits,key=lambda x:-x[1]): files[f]=txt(f)[:at]+s+txt(f)[at:]
for f,t in files.items(): (d/f).write_text(t)
p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True)
errs=[l for l in (p.stdout+p.stderr).splitlines() if l.strip().startswith("[error]")]
print(f"{S}.{E} -> {T}.{A} [{','.join(EVS)}]: {len(errs)} errors"); [print("   ",l[:170]) for l in errs[:6]]
