#!/usr/bin/env python3
"""B3: `index on field Stored<X>.<x>Id` states a UNIQUE natural key, not an
index -- one row per value. Convert those; leave a foreign id (many rows per
value, `customerId` on orders) as an index. riddl's clause order is strict
(`of`, `link`, `key on`, `index on`), so each schema's lines are reordered.

    ./scripts/schema-keys.py [--dry]
"""
import re,sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models")
dry="--dry" in sys.argv
def lc(s): return s[0].lower()+s[1:]
changed=keys=0; files=0
for f in sorted(ROOT.rglob("*.riddl")):
    if "patterns" in f.parts or "/1/" in str(f): continue
    lines=f.read_text().split("\n"); out=[]; hit=False
    for l in lines:
        m=re.match(r"^(\s*)index on field ([A-Za-z]+)\.([A-Za-z]+)\s*$",l)
        if m:
            ind,rec,fld=m.groups()
            base=rec[6:] if rec.startswith("Stored") else rec
            if fld==lc(base)+"Id":
                out.append(f"{ind}key on field {rec}.{fld}"); hit=True; keys+=1; continue
        out.append(l)
    if not hit: continue
    # strict order: within each `of ... as record R` group, key-on lines before index-on
    res=[]; i=0
    while i<len(out):
        l=out[i]
        if re.match(r"^\s*of \w+ as record ",l):
            j=i+1; block=[]
            while j<len(out) and re.match(r"^\s*(key|index) on field ",out[j]): block.append(out[j]); j+=1
            ks=[b for b in block if "key on" in b]; ix=[b for b in block if "index on" in b]
            res.append(l); res.extend(ks+ix); i=j; continue
        res.append(l); i+=1
    if res!=lines:
        files+=1; changed+=1
        if not dry: f.write_text("\n".join(res))
print(f"{keys} indices became keys in {files} files")
