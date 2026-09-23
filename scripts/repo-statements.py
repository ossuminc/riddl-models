#!/usr/bin/env python3
"""B2: the repository storage statements. Turn the `do` prose that describes a
row write into the statement that IS one, typed against the schema.

  do "insert row into S.T with a, b, c"     -> store record StoredX(...) in S.T
  do "update S.T set col = f where k matches" -> update S.T set col = <b>.f where k == <b>.k
  do "update S.T where k matches"           -> (no columns named) left as prose
  do "apply E to the stored row"            -> update, from the command's own fields

Column sources come from the handled Persist command: a command field whose
name matches a stored column is that column's value; `set col = f` names the
pair explicitly. The key is the schema's `key on field` (B3), or the stored
record's identity field.

    ./scripts/repo-statements.py [--dry] [model-dir ...]
"""
import json,re,subprocess,sys,collections
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
dry="--dry" in sys.argv
args=[a for a in sys.argv[1:] if not a.startswith("--")]
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
def lc(s): return s[0].lower()+s[1:]
stats=collections.Counter(); notes=[]
models=[ROOT/a for a in args] if args else sorted({c.parent for c in ROOT.rglob("*.conf") if "patterns" not in c.parts and "/1/" not in str(c)})
for d in models:
    conf=next(d.glob("*.conf"),None)
    if not conf: continue
    m=re.search(r'input-file\s*=\s*"([^"]+)"',conf.read_text())
    if not m: continue
    e=m.group(1)
    p=subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True)
    try: ns=list(nodes(json.loads(p.stdout)))
    except Exception: notes.append(f"{d.relative_to(ROOT)}: dump failed"); continue
    byp={n["path"]:n for n in ns if "path" in n}
    fields=collections.defaultdict(list)
    for n in ns:
        if n["kind"]=="field": fields[n["parent"]].append(n["id"])
    texts={}
    def text(f):
        fp=(d/e).parent.joinpath(f).resolve()
        if fp not in texts: texts[fp]=fp.read_text()
        return fp
    edits=collections.defaultdict(list)
    for repo in [n for n in ns if n["kind"]=="repository"]:
        schema=next((n for n in ns if n["kind"]=="schema" and n["parent"]==repo["path"]),None)
        if not schema: continue
        fp=text(schema["file"]); st=texts[fp]; s=schema["span"]["start"]["offset"]
        head=st[s:st.find("\n with {",s) if "\n with {" in st[s:s+2000] else s+1200]
        tables=dict(re.findall(r"of (\w+) as record ([\w.]+)",head))       # table -> record
        keys=dict((a.split(".")[-1],b) for a,b in re.findall(r"key on field ([\w.]+)\.(\w+)",head))  # record -> key field
        sname=schema["id"]
        if not tables: continue
        # the record for a table, and its columns
        def cols(rec):
            r=next((n for n in ns if n["kind"]=="record" and n["id"]==rec.split(".")[-1]),None)
            return set(fields.get(r["path"],[])) if r else set()
        for cl in [n for n in ns if n["kind"]=="onmessageclause" and repo["path"] in n.get("ancestors",[])]:
            cmd=byp.get(cl["message"]["resolved"])
            if not cmd or cmd["kind"]!="command": continue
            cfields=fields.get(cmd["path"],[])
            fp=text(cl["file"]); t=texts[fp]; s=cl["span"]["start"]["offset"]; en=brace_end(t,s); body=t[s:en]
            dm=re.search(r'(\s*)do "(.*?)"',body,re.S)
            if not dm: continue
            prose=" ".join(dm.group(2).split()); indent=dm.group(1).lstrip("\n")
            b=cl.get("binding") or lc(cmd["id"])
            # which table?
            tm=re.search(r"(?:into|update|from)\s+(?:\w+\.)?(\w+)",prose)
            table=tm.group(1) if tm and tm.group(1) in tables else None
            if not table:
                # `apply <Event> to the stored row` names none. The row is the one for
                # the entity that YIELDED the event the command is named for -- a
                # repository may store several, and picking the first inverts them.
                evname=cmd["id"][7:] if cmd["id"].startswith("Persist") else None
                evn=next((n for n in ns if n["kind"]=="event" and n["id"]==evname),None)
                own=byp.get(evn["parent"],{}).get("id") if evn else None
                table=next((tb for tb,rc in tables.items() if rc.split(".")[-1]=="Stored"+str(own)),None)
                if not table:
                    cands=[tb for tb,rc in tables.items() if rc.split(".")[-1].startswith("Stored")]
                    table=cands[0] if len(cands)==1 else None
            if not table: stats["no table"]+=1; continue
            rec=tables[table]; rcols=cols(rec); key=keys.get(rec.split(".")[-1])
            if not key or key not in cfields: stats["no key on the command"]+=1; continue
            stmt=None
            if prose.startswith("insert"):
                named=[x.strip().rstrip(".") for x in re.split(r",?\s+and\s+|,\s*",re.search(r"with (.*)$",prose).group(1))] if "with " in prose else []
                args_=[c for c in cfields if c in rcols]
                missing=sorted(rcols-set(args_))
                ctor=", ".join([f"{c} = {b}.{c}" for c in args_]+[f'{c} = prompt("the {c} of this row")' for c in missing])
                stmt=f"store record {rec.split('.')[-1]}({ctor}) in {sname}.{table}"
                stats["store"]+=1
            elif prose.startswith("update") or prose.startswith("apply"):
                pairs=[]
                for a_,f_ in re.findall(r"(\w+)\s*=\s*(\w+)",prose):
                    if a_ in rcols and f_ in cfields: pairs.append((a_,f_))
                if not pairs:
                    pairs=[(c,c) for c in cfields if c in rcols and c!=key]
                if not pairs: stats["update names no column"]+=1; continue
                sets=", ".join(f"{a_} = {b}.{f_}" for a_,f_ in pairs)
                stmt=f"update {sname}.{table} set {sets} where {key} == {b}.{key}"
                stats["update"]+=1
            else:
                stats["other prose"]+=1; continue
            # the clause head gains its binding if it had none
            newbody=body
            if not cl.get("binding"):
                newbody=re.sub(r"^(\s*)on command ",rf"\1on {b}: command ",newbody,count=1)
            newbody=newbody[:newbody.index('do "')]+stmt+newbody[newbody.index('"',newbody.index('do "')+4)+1:]
            edits[fp].append((s,en,newbody))
    for fp,es in edits.items():
        t=texts[fp]
        for s,en,new in sorted(es,key=lambda x:x[0],reverse=True): t=t[:s]+new+t[en:]
        if not dry: fp.write_text(t)
print(dict(stats))
for n in notes[:10]: print("  ",n)
