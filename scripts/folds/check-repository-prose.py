#!/usr/bin/env python3
"""riddlg's 'Refuse to ask the AI for a row nobody can build', approximated:
for every repository Persist clause, the lowerCamel tokens in its `do` prose
that are neither a field of the handled command nor of the schema's record."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
D=ROOT/(sys.argv[1] if len(sys.argv)>1 else "hospitality/food-service/reactive-bbq")
E=re.search(r'input-file\s*=\s*"([^"]+)"',next(D.glob("*.conf")).read_text()).group(1)
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
d=json.loads(subprocess.run([R,"dump",E,"--json"],cwd=D,capture_output=True,text=True).stdout)
ns=list(nodes(d)); byp={n["path"]:n for n in ns if "path" in n}
fields={}
for n in ns:
    if n["kind"]=="field": fields.setdefault(n["parent"],set()).add(n["id"])
STOP={"where","matches","set","with","and","into","row","insert","update","append","remove","from","to","in","array","record","the","a","of","stored","apply","current","state","projection","for","then","by","as","or","is","this","that","new","negative"}
flagged=0; clauses=0
for repo in [n for n in ns if n["kind"]=="repository"]:
    schema=next((n for n in ns if n["kind"]=="schema" and n["parent"]==repo["path"]),None)
    rec=None
    if schema:
        t=(D/schema["file"]).read_text(); ms=re.search(r"as record (\S+)",t[schema["span"]["start"]["offset"]:schema["span"]["start"]["offset"]+400])
        rec=next((n for n in ns if n["kind"]=="record" and n["id"]==ms.group(1).split(".")[-1]),None) if ms else None
    rf=fields.get(rec["path"],set()) if rec else set()
    tables=set(re.findall(r"of (\w+) as record",(D/schema["file"]).read_text()[schema["span"]["start"]["offset"]:schema["span"]["start"]["offset"]+400])) if schema else set()
    rf=rf|tables   # a table name is not a column riddlg needs to fill
    for cl in [n for n in ns if n["kind"]=="onmessageclause" and repo["path"] in n.get("ancestors",[])]:
        cmd=byp.get(cl["message"]["resolved"])
        if not cmd or not cmd["id"].startswith("Persist"): continue
        t=(D/cl["file"]).read_text(); s=cl["span"]["start"]["offset"]; body=t[s:brace_end(t,s)]
        m=re.search(r'do "(.*?)"',body,re.S)
        if not m: continue
        clauses+=1
        toks={x for x in re.findall(r"\b[a-z][a-zA-Z0-9]*\b",m.group(1)) if re.search(r"[A-Z]",x) and x not in STOP}
        missing=sorted(toks-fields.get(cmd["path"],set())-rf)
        if missing: flagged+=1; print(f"{repo['id']}.{cmd['id']}: {missing}")
print(f"{flagged} of {clauses} clauses name a field nothing declares")
