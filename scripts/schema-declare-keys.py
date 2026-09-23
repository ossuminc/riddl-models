#!/usr/bin/env python3
"""B3, the other half: a `Stored<X>` record with an `<x>Id` field and no
`key on` line has an identity the schema never declares, so nothing can say
WHICH row an update writes. Declare it. (schema-keys.py converted the indices
that already existed; this adds the ones that never did.)

    ./scripts/schema-declare-keys.py [--dry] [model-dir ...]
"""
import re,sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models")
dry="--dry" in sys.argv
args=[a for a in sys.argv[1:] if not a.startswith("--")]
roots=[ROOT/a for a in args] if args else [ROOT]
def lc(s): return s[0].lower()+s[1:]
BODY=r"((?: +of \w+ as record [\w.]+(?: with history)?\n| +link [^\n]+\n| +(?:key|index) on field [\w.]+\n)+)"
n=0
for root in roots:
    for f in sorted(root.rglob("*.riddl")):
        if "patterns" in f.parts or "/1/" in str(f): continue
        t=f.read_text(); orig=t
        while True:
            target=None
            for m in re.finditer(r"\n( +)schema (\w+) is relational\n"+BODY,t):
                ind,sname,body=m.groups()
                keyed={x for x in re.findall(r"key on field (\w+)\.",body)}
                for tbl,rc in re.findall(r"of (\w+) as record ([\w.]+)",body):
                    rec=rc.split(".")[-1]
                    if rec in keyed or not rec.startswith("Stored"): continue
                    idf=lc(rec[6:])+"Id"
                    # the record must actually declare it
                    if not re.search(r"\n +record "+rec+r" is \{(?:.|\n)*?\n +"+idf+r": ",t): continue
                    target=(m,ind,body,rec,idf); break
                if target: break
            if not target: break
            m,ind,body,rec,idf=target
            lines=[l for l in body.split("\n") if l.strip()]
            ofl=[l for l in lines if " of " in l]; lk=[l for l in lines if " link " in l]
            ks=[l for l in lines if "key on" in l]; ix=[l for l in lines if "index on" in l]
            ks.append(f"{ind}  key on field {rec}.{idf}")
            t=t[:m.start(3)]+"\n".join(ofl+lk+ks+ix)+"\n"+t[m.end(3):]
            n+=1
        if t!=orig and not dry: f.write_text(t)
print(f"{n} identity keys declared")
