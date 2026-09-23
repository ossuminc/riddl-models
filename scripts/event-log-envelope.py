#!/usr/bin/env python3
"""B1: an `<Entity>EventLog` flow forwards every entity event to the repository
as `Log<Entity>Event`, and said so with a prompt because the clause could not
read the message. Under `on other as m` it can: `m.type` is the message's type
name and `m.<field>` falls through the envelope to the message when every member
carries it. One `option message_envelope` per enclosing context.

    ./scripts/event-log-envelope.py <model-dir>
"""
import re,sys
from pathlib import Path
D=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
pat=re.compile(r'( *)on other is \{\n'
               r' *let (\w+): type (\w+) = prompt\("[^"]*"\)\n'
               r' *send \2 to outlet ([\w.]+)\n'
               r' *do "append [^"]*"\n'
               r' *\}')
def cmd_fields(name):
    """the Log command's id field and event-type field, from its own block"""
    for g in D.rglob("*.riddl"):
        s=g.read_text(); m=re.search(r"\n  +command "+name+r" is \{",s)
        if not m: continue
        depth=0; i=s.index("{",m.start()); j=i
        while j<len(s):
            if s[j]=="{": depth+=1
            elif s[j]=="}":
                depth-=1
                if depth==0: break
            j+=1
        block=s[i:j]
        fs=re.findall(r"\n    (\w+): ",block)
        idf=next((f for f in fs if f.endswith("Id")),None)
        tyf=next((f for f in fs if f.endswith("EventType")),None)
        return idf,tyf
    return None,None
n=0; touched=set()
for f in sorted(D.rglob("*.riddl")):
    t=f.read_text(); out=[]; last=0; hit=False
    for m in pat.finditer(t):
        ind,binding,cmd,outlet=m.groups()
        idf,tyf=cmd_fields(cmd)
        if not idf or not tyf: print("  skip",cmd,"(fields",idf,tyf,")"); continue
        base=idf[6:] if idf.startswith("logged") else idf
        msgid=base[0].lower()+base[1:]
        out.append(t[last:m.start()])
        out.append(f'{ind}on other as m is {{\n'
                   f'{ind}  send command {cmd}({idf} = m.{msgid}, {tyf} = m.type) to outlet {outlet}\n'
                   f'{ind}}}')
        last=m.end(); n+=1; hit=True
    if hit:
        out.append(t[last:]); t="".join(out); f.write_text(t); touched.add(f)
for f in sorted(touched):
    t=f.read_text()
    if "option message_envelope" in t: continue
    m=re.search(r"\n\} with \{\n",t)
    if not m: print("  no context with-block in",f.name); continue
    f.write_text(t[:m.end()]+'  option message_envelope("Riddl.Envelope")\n'+t[m.end():])
print(f"{n} event-log flows read the envelope, in {len(touched)} files")
