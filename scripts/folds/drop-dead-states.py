#!/usr/bin/env python3
"""Delete a state nothing enters and nothing handles, and its record.
    ./scripts/folds/drop-dead-states.py <model> <Entity> <State> [<State>…]
Refuses if anything but the state's own declaration names the state or its
record (grep over the model), or if the state's handler has any clause but
`on init`."""
import re,sys,subprocess
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models")
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
d=ROOT/sys.argv[1]; ent=sys.argv[2]
fp=d/f"{ent}.riddl"; t=fp.read_text()
for st in sys.argv[3:]:
    m=re.search(r"^[ \t]*(?:initial )?state "+st+r" of (?:record )?([\w.]+) is \{",t,re.M)
    if not m: print(f"{st}: not found"); continue
    rec=m.group(1).split(".")[-1]
    s=m.start(); en=block_end(t,s); body=t[s:en]
    clauses=re.findall(r"^\s*on (?!init\b)\S+",body,re.M)
    if clauses: print(f"{st}: handles {clauses}; refusing"); continue
    def offs(txt):
        o=0
        for l in txt.split("\n"): yield o,l; o+=len(l)+1
    others=[str(f.relative_to(d))+":"+str(i+1) for f in d.rglob("*.riddl") for i,(o,l) in enumerate(offs(f.read_text())) if re.search(r"\b"+st+r"\b|\b"+rec+r"\b",l) and not (f==fp and s<=o<en)]
    others=[o for o in others if not re.search(r"record "+rec+r" is",open(d/o.split(":")[0]).read().split("\n")[int(o.split(":")[1])-1])]
    if others: print(f"{st}: referenced elsewhere {others[:5]}; refusing"); continue
    t=t[:s]+t[en:]
    mr=re.search(r"^[ \t]*record "+rec+r" is \{",t,re.M)
    if mr: rs=mr.start(); t=t[:rs]+t[block_end(t,rs):]
    print(f"{st}: deleted with record {rec}")
fp.write_text(t)
