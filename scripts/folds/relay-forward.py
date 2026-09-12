#!/usr/bin/env python3
"""A boundary clause relaying a command that declares `yields` must `forward`,
not `send` (`msg-yield-undeclared` otherwise). For each such error riddlc
reports on a model, rewrite `send <b> to outlet` -> `forward <b> to outlet`
in that clause."""
import re,subprocess,sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
def entry(d):
    for c in d.glob("*.conf"):
        m=re.search(r'input-file\s*=\s*"([^"]+)"',c.read_text())
        if m: return m.group(1)
for model in sys.argv[1:]:
    d=ROOT/model; e=entry(d)
    p=subprocess.run([R,"--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True); out=p.stdout+p.stderr
    hits=re.findall(r"^\[error\] \[msg-yield-undeclared\] (\S+?)\((\d+):",out,re.M)
    byfile={}
    for f,ln in hits: byfile.setdefault(f,set()).add(int(ln))
    n=0
    for f,lines in byfile.items():
        fp=(d/e).parent/f; L=fp.read_text().split("\n")
        for ln in lines:
            i=ln  # clause head at ln-1; statements follow until the closing brace
            while i<len(L) and not re.match(r"\s*}\s*$",L[i]):
                m=re.match(r"(\s*)send (\w+) to outlet (.*)$",L[i])
                if m: L[i]=f"{m.group(1)}forward {m.group(2)} to outlet {m.group(3)}"; n+=1
                i+=1
        fp.write_text("\n".join(L))
    p=subprocess.run([R,"--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True); out=p.stdout+p.stderr
    print(f"{model}: {n} sends -> forwards; errors left: {len(re.findall(r'^\[error\]',out,re.M))}")
