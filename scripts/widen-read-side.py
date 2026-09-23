#!/usr/bin/env python3
"""BACKLOG #40, the next B2 tranche: outside reactive-bbq every repository
clause says `apply <Event> to the stored row` over a `Persist<Event>` command
carrying only the id and a `Stored<X>` record declaring only the id. There is
nothing to state because there is nothing there.

Widen it from the EVENT the command is named for: every field of `<Event>`
becomes a field of `Persist<Event>` (optional if it is not the id), and a
column of `Stored<X>` (optional unless the creating event carries it). Then
`repo-statements.py` turns the prose into `store`/`update`.

The projector that tells the command passes the new fields from the event.

    ./scripts/widen-read-side.py [--dry] [model-dir ...]
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
def paren_end(txt,i):
    depth=0; ins=False; j=i
    while j<len(txt):
        ch=txt[j]
        if ch=='"' and txt[j-1]!="\\": ins=not ins
        elif not ins:
            if ch=="(": depth+=1
            elif ch==")":
                depth-=1
                if depth==0: return j+1
        j+=1
    return len(txt)
def words(s): return re.sub(r"(?<!^)(?=[A-Z])"," ",s).lower()
def lc(s): return s[0].lower()+s[1:]
stats=collections.Counter()
models=[ROOT/a for a in args] if args else sorted({c.parent for c in ROOT.rglob("*.conf") if "patterns" not in c.parts and "/1/" not in str(c)})
for d in models:
    conf=next(d.glob("*.conf"),None)
    if not conf: continue
    m=re.search(r'input-file\s*=\s*"([^"]+)"',conf.read_text())
    if not m: continue
    e=m.group(1)
    p=subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True)
    try: ns=list(nodes(json.loads(p.stdout)))
    except Exception: stats["dump failed"]+=1; continue
    byp={n["path"]:n for n in ns if "path" in n}
    fields=collections.defaultdict(list)
    for n in ns:
        if n["kind"]=="field": fields[n["parent"]].append(n)
    texts={}
    def text(f):
        fp=((d/e).parent/f).resolve()
        if fp not in texts: texts[fp]=fp.read_text()
        return fp
    def src_type(fn):
        fp=text(fn["file"]); t=texts[fp]; s=fn["span"]
        src=t[s["start"]["offset"]:s["end"]["offset"]]
        mm=re.match(r"\s*"+re.escape(fn["id"])+r"\s*:\s*(.*?)\s*(?:with\s*\{.*)?$",src,re.S)
        return (mm.group(1).strip() if mm else fn["type"].replace("type ","")).rstrip()
    events={n["id"]:n for n in ns if n["kind"]=="event"}
    edits=collections.defaultdict(list)
    newcmd=collections.defaultdict(list)   # command path -> [(name,type,evfield)]
    newcol=collections.defaultdict(list)   # record path -> [(name,type)]
    for repo in [n for n in ns if n["kind"]=="repository"]:
        schema=next((n for n in ns if n["kind"]=="schema" and n["parent"]==repo["path"]),None)
        if not schema: continue
        fp=text(schema["file"]); st=texts[fp]; s=schema["span"]["start"]["offset"]
        head=st[s:s+1500]
        tables=dict(re.findall(r"of (\w+) as record ([\w.]+)",head))
        if not tables: continue
        recs={rc.split(".")[-1]:next((n for n in ns if n["kind"]=="record" and n["id"]==rc.split(".")[-1] and n["parent"]==repo["path"]),None) for rc in tables.values()}
        for cl in [n for n in ns if n["kind"]=="onmessageclause" and repo["path"] in n.get("ancestors",[])]:
            cmd=byp.get(cl["message"]["resolved"])
            if not cmd or cmd["kind"]!="command" or not cmd["id"].startswith("Persist"): continue
            fp2=text(cl["file"]); t2=texts[fp2]; cs=cl["span"]["start"]["offset"]
            body=t2[cs:brace_end(t2,cs)]
            if not re.search(r'do "apply \w+ to the stored row"',body): continue
            ev=events.get(cmd["id"][7:])
            if not ev: stats["no event for command"]+=1; continue
            # the row this event belongs to: `Stored<Entity that yielded it>`
            owner=byp.get(ev["parent"],{})
            rec=recs.get("Stored"+owner.get("id",""))
            if not rec:
                stats["no Stored record for "+owner.get("id","?")]+=1; continue
            rcols={f["id"] for f in fields[rec["path"]]}
            cf={f["id"] for f in fields[cmd["path"]]}
            for f in fields[ev["path"]]:
                ty=src_type(f)
                if f["id"] not in cf and f["id"] not in [a for a,_,_ in newcmd[cmd["path"]]]:
                    newcmd[cmd["path"]].append((f["id"],ty if ty.endswith(("?","*","+")) else ty+"?",f["id"]))
                if f["id"] not in rcols and f["id"] not in [a for a,_ in newcol[rec["path"]]]:
                    newcol[rec["path"]].append((f["id"],ty if ty.endswith(("?","*","+")) else ty+"?"))
            stats["clauses widened"]+=1
    def ins_fields(nodepath,fs,kind):
        n=byp[nodepath]; fp=text(n["file"]); t=texts[fp]
        s=n["span"]["start"]["offset"]; en=brace_end(t,s); at=t.rfind("\n",s,en)+1
        ind=re.match(r"\s*",t[at:]).group(0)
        decl="".join(f'{ind}  {a}: {ty} with {{\n{ind}    briefly "{words(a).capitalize()}"\n'
                     f'{ind}    described as {{\n{ind}      |{kind}\n{ind}    }}\n{ind}  }}\n' for a,ty in fs)
        edits[fp].append((at,at,decl))
    for cp,fs in newcmd.items():
        ins_fields(cp,[(a,ty) for a,ty,_ in fs],"Carried from the event the projector folded, so the row can hold it.")
        cmd=byp[cp]
        for rf in d.rglob("*.riddl"):
            rfp=text(str(rf.relative_to((d/e).parent)) if (d/e).parent in rf.parents else rf.name)
            rt=texts[rfp]
            for mm in re.finditer(r"\b"+re.escape(cmd["id"])+r"\(",rt):
                j=paren_end(rt,mm.end()-1); inner=rt[mm.end():j-1]
                mb=re.search(r"=\s*(\w+)\.\w+",inner); evb=mb.group(1) if mb else None
                add=[f"{a} = {evb}.{src}" if evb else f'{a} = prompt("the {words(a)}")' for a,_,src in fs if not re.search(r"\b"+a+r"\s*=",inner)]
                if add: edits[rfp].append((j-1,j-1,(", " if inner.strip() else "")+", ".join(add)))
    for rp,fs in newcol.items():
        ins_fields(rp,fs,"As the persisting projector last wrote it.")
    if dry: continue
    for fp,es in edits.items():
        t=texts[fp]
        for s,en,new in sorted(es,key=lambda x:x[0],reverse=True): t=t[:s]+new+t[en:]
        fp.write_text(t)
print(dict(stats))
