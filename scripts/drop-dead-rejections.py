#!/usr/bin/env python3
"""BACKLOG #24, the rest: reactive-bbq's `<Command>Rejected` events that nothing
yields or sends any more (the state-guard sends were removed in 42c1d161; the
declarations, folds, split clauses and alternation members were left). riddlc
-50's `entity-event-sourced-prose-folds` now counts their folds as holes.

Reads `riddlc dump --json`, then for every Rejected event with no send/yield:
  - deletes its on-event clauses (entity folds, split fan-outs, emitters)
  - trims it out of every `one of` alternation that names it
  - deletes the declaration
  - rewrites the projectors' `do "not persisted: …"` lists without it
Keeps any Rejected event that IS produced (RedeemPointsRejected).
"""
import json,re,subprocess,sys,collections
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
D=ROOT/"hospitality/food-service/reactive-bbq"; E="reactive-bbq.riddl"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
def brace_end(txt,start):
    i=txt.index("{",start); depth=0; ins=False; j=i
    while j<len(txt):
        ch=txt[j]
        if ch=='"' and txt[j-1]!="\\": ins=not ins
        elif not ins:
            if ch=="{": depth+=1
            elif ch=="}":
                depth-=1
                if depth==0: return j+1
        j+=1
    return len(txt)
def block_end(txt,start):
    j=brace_end(txt,start)
    m=re.match(r"\s*with\s*\{", txt[j:])
    if m: j=brace_end(txt,j+m.end()-1)
    nl=txt.find("\n",j); return nl+1 if nl>=0 else len(txt)
def line_start(txt,off):
    return txt.rfind("\n",0,off)+1
d=json.loads(subprocess.run([R,"dump",E,"--json"],cwd=D,capture_output=True,text=True).stdout)
ns=list(nodes(d)); byp={n["path"]:n for n in ns if "path" in n}
dead={n["path"]:n for n in ns if n["kind"]=="event" and n["id"].endswith("Rejected")}
# which are produced?
produced=set()
def walk(n,top):
    if isinstance(n,dict):
        if n.get("kind"): top=n
        for k,v in n.items():
            if k=="resolved" and isinstance(v,str) and v in dead and top["kind"] in("send-statement","yield-statement","tell-statement","let-statement"): produced.add(v)
            walk(v,top)
    elif isinstance(n,list):
        for v in n: walk(v,top)
walk(d,{"kind":"root"})
for p in produced: print("keeping (produced):",p); dead.pop(p)
deadnames={p.split(".")[-1] for p in dead}
edits=collections.defaultdict(list)   # file -> [(start,end,replacement)]
files={}
def text(f):
    fp=(D/E).parent/f
    if fp not in files: files[fp]=fp.read_text()
    return fp,files[fp]
# 1. declarations and on-event clauses
for n in ns:
    if n["kind"]=="event" and n["path"] in dead:
        fp,t=text(n["file"]); s=line_start(t,n["span"]["start"]["offset"]); edits[fp].append((s,block_end(t,s),""))
    elif n["kind"]=="on-event" and n["message"]["resolved"] in dead:
        fp,t=text(n["file"]); s=line_start(t,n["span"]["start"]["offset"]); e=brace_end(t,s); nl=t.find("\n",e); edits[fp].append((s,nl+1,""))
# 2. alternation members
for n in ns:
    if n["kind"]=="type" and n.get("type","").startswith("one of"):
        fp,t=text(n["file"]); s=n["span"]["start"]["offset"]; e=brace_end(t,s); body=t[s:e]
        m=re.search(r"\{(.*)\}",body,re.S)
        if not m: continue
        members=[x.strip() for x in m.group(1).split(" or ")]
        keep=[x for x in members if x.split(".")[-1] not in deadnames]
        if len(keep)==len(members): continue
        if not keep: print("WARNING: alternation emptied",n["path"]); continue
        if len(keep)==1: print("NOTE: alternation down to one member",n["path"],keep)
        new=body[:m.start(1)]+"\n    "+" or ".join(keep)+"\n  "+body[m.end(1):]
        edits[fp].append((s,e,new))
# 3. "not persisted" prose: rebuild from what the handler's owner can receive minus what it handles
for n in ns:
    if n["kind"]=="handler":
        clauses=[c for c in ns if c["kind"]=="on-event" and c["parent"]==n["path"]]
        handled={c["message"]["resolved"] for c in clauses}
        owner=byp.get(n["parent"]);
        if not owner: continue
        inlets=[i for i in ns if i["kind"]=="inlet" and i["parent"]==owner["path"]]
        members=set()
        for i in inlets:
            ty=i.get("type") if isinstance(i.get("type"),dict) else {}
            alt=ty.get("alternation")
            if alt:
                for m in alt: members.add(m["resolved"])
            elif ty.get("resolved"): members.add(ty["resolved"])
        fp,t=text(n["file"]); s=n["span"]["start"]["offset"]; e=brace_end(t,s); body=t[s:e]
        mm=re.search(r'do "not persisted: [^"]*"',body)
        if not mm: continue
        rest=sorted({p.split(".")[-1] for p in members if p not in handled and p not in dead and byp.get(p,{}).get("kind")=="event"})
        if not rest: new='do "nothing else arrives: every member of the inlet alternation has its own clause"'
        else:
            head=", ".join(rest[:4]); more=len(rest)-4
            new=f'do "not persisted: {head}{f" and {more} more" if more>0 else ""} record{"s" if len(rest)==1 else ""} no stored state"'
        edits[fp].append((s+mm.start(),s+mm.end(),new))
for fp,es in edits.items():
    t=files[fp]
    for s,e,new in sorted(es,reverse=True):
        t=t[:s]+new+t[e:]
    fp.write_text(t)
    print(f"{fp.relative_to(ROOT)}: {len(es)} edits")
print(f"dropped {len(dead)} events: {sorted(deadnames)}")
