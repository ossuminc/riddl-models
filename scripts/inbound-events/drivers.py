#!/usr/bin/env python3
"""Driver map: for each external command a model sends, which LOCAL clause sends it.

    python3 scripts/inbound-events/drivers.py <model-dir> [<model-dir> ...]

Used to apply the circularity rule from BACKLOG #36: a tell is circular when
the command that caused the external act is the one that would record it.
The digest says WHICH of our commands cause an event; this says FROM WHERE,
which is what decides. Text-based on purpose -- it reads `on` heads and
`type X.Y = prompt` / `tell command X.Y` lines -- so it is a reading aid, not
a gate; anything it decides is re-checked by apply.py's per-model validate.
"""
import re,glob,sys
for m in sys.argv[1:]:
    print("###",m)
    exts=set()
    for f in glob.glob(m+"/*.riddl"):
        exts|=set(re.findall(r'external context (\w+)',open(f).read()))
    for f in sorted(glob.glob(m+"/*.riddl")):
        txt=open(f).read(); clause=None; proc=None
        for line in txt.splitlines():
            p=re.match(r'\s*(?:\w+ )*(entity|adaptor|projector|streamlet|context|saga) (\w+)',line)
            if p: proc=p.group(2)
            h=re.match(r'\s*on (?:\w+: )?(command|event|query|init|other|result) ([\w.]+)',line)
            if h: clause=f"{h.group(1)} {h.group(2).split('.')[-1]}"
            for t in re.finditer(r'(?:type|tell command) (\w+)\.(\w+)',line):
                if t.group(1) in exts and clause and not re.search(r'(Result|Request|Command|Response|Results|Status|Info|Details|List|Data)$',t.group(2)) and 'other' not in clause:
                    print(f"   {clause:34s} -> {t.group(1)}.{t.group(2)}")
