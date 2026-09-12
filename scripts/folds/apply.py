#!/usr/bin/env python3
"""Turn each decisions.tsv row into a real fold.

    model<TAB>Entity<TAB>Event<TAB>State<TAB>stmt; stmt; …
    stmt = f=expr            set field <Entity>.<State>.<f> to <expr>
         | +f:Type=expr      first add `f: Type` to the state's record (and
                             `f = empty` to every constructor of it), then set
    `e.` in an expr is the event; the clause gets a lowerCamel binding.

Reads `riddlc dump --json` for spans; edits by offset; validates each model
after and reports the finding counts before/after.
"""
import json,re,subprocess,sys,collections
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
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
def entry(d):
    for c in d.glob("*.conf"):
        m=re.search(r'input-file\s*=\s*"([^"]+)"',c.read_text())
        if m: return m.group(1)
def words(s): return re.sub(r"(?<!^)(?=[A-Z])"," ",s).lower()
def lc(s): return s[0].lower()+s[1:]
def findings(d,e):
    p=subprocess.run([R,"--no-ansi-messages","--provide-tips","validate",e],cwd=d,capture_output=True,text=True)
    out=p.stdout+p.stderr
    return collections.Counter(re.findall(r"^\[(\w+)\] \[([\w-]+)\]",out,re.M)), out
rows=collections.defaultdict(list)
for line in open(ROOT/"scripts/folds/decisions.tsv"):
    if not line.strip() or line.startswith("#"): continue
    model,ent,ev,st,stmts=line.rstrip("\n").split("\t")
    rows[model].append((ent,ev,st,stmts))
only=set(sys.argv[1:])
for model,rs in rows.items():
    if only and model not in only: continue
    d=ROOT/model; e=entry(d)
    before,_=findings(d,e)
    dump=json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout)
    ns=list(nodes(dump)); byp={n["path"]:n for n in ns if "path" in n}
    texts={}
    def text(f):
        fp=((d/e).parent/f).resolve()
        if fp not in texts: texts[fp]=fp.read_text()
        return fp
    edits=collections.defaultdict(list)
    newfields=collections.defaultdict(list)   # record path -> [(name,type)]
    for ent,ev,st,stmts in rs:
        entn=next(n for n in ns if n["kind"]=="entity" and n["id"]==ent)
        stn=next(n for n in ns if n["kind"]=="state" and n["id"]==st and n["parent"]==entn["path"])
        fp=text(stn["file"]); t=texts[fp]
        mm=re.match(r"\s*(?:initial )?state \S+ of (?:record )?(\S+)",t[stn["span"]["start"]["offset"]:]); rec=mm.group(1).split(".")[-1]
        recn=next((n for n in ns if n["kind"] in("record","type") and n["id"]==rec and n["parent"]==entn["path"]),None) or next(n for n in ns if n["kind"] in("record","type") and n["id"]==rec)
        cl=next(n for n in ns if n["kind"]=="on-event" and n["message"]["resolved"].split(".")[-1]==ev and entn["path"] in n["ancestors"])
        cfp=text(cl["file"]); ct=texts[cfp]; s=cl["span"]["start"]["offset"]; s=ct.rfind("\n",0,s)+1; en=brace_end(ct,s)
        head=ct[s:ct.index("{",s)]
        mb=re.search(r"on (\w+): event",head); binding=mb.group(1) if mb else lc(ev)
        indent=re.match(r"\s*",ct[s:]).group(0)
        lines=[]
        for stmt in [x.strip() for x in stmts.split(";") if x.strip()]:
            m=re.match(r"(\+?)([\w.]+)(?::([^=]+))?=(.*)$",stmt)
            plus,f,ty,expr=m.groups()
            if plus:
                if (f,ty.strip()) not in newfields[recn["path"]]: newfields[recn["path"]].append((f,ty.strip()))
            expr=re.sub(r"\be\.",binding+".",expr.strip())
            lines.append(f"{indent}  set field {ent}.{st}.{f} to {expr}")
        new=f"{indent}on {binding}: event {ev} is {{\n"+"\n".join(lines)+f"\n{indent}}}"
        edits[cfp].append((s,en,new))
    # new fields: declare in the record, and `= empty` in every constructor of it across the model
    for recp,fs in newfields.items():
        recn=byp[recp]; fp=text(recn["file"]); t=texts[fp]; s=recn["span"]["start"]["offset"]; en=brace_end(t,s)
        # insert before the closing brace of the record body
        ins=t.rfind("}",s,en)
        decl="".join(f'    {f}: {ty} with {{\n      briefly "{words(f).capitalize()}"\n    }}\n' for f,ty in fs)
        edits[fp].append((ins,ins,decl))
        rec=recn["id"]
        for rf in d.rglob("*.riddl"):
            rt=rf.read_text()
            if rec+"(" not in rt: continue
            rfp=rf.resolve()
            if rfp not in texts: texts[rfp]=rt
            for m in re.finditer(re.escape(rec)+r"\(",texts[rfp]):
                # find the matching close paren
                j=m.end(); depth=1; ins_=False
                while depth and j<len(texts[rfp]):
                    ch=texts[rfp][j]
                    if ch=='"' and texts[rfp][j-1]!="\\": ins_=not ins_
                    elif not ins_:
                        if ch=="(": depth+=1
                        elif ch==")": depth-=1
                    j+=1
                close=j-1
                add=", ".join(f"{f} = empty" for f,ty in fs)
                body=texts[rfp][m.end():close].strip()
                edits[rfp].append((close,close,(", " if body else "")+add))
    for fp,es in edits.items():
        t=texts[fp]
        for s,en,new in sorted(es,key=lambda x:x[0],reverse=True): t=t[:s]+new+t[en:]
        fp.write_text(t)
    after,out=findings(d,e)
    delta={k:(before.get(k,0),after.get(k,0)) for k in set(before)|set(after) if before.get(k,0)!=after.get(k,0)}
    errs=[l for l in out.splitlines() if l.startswith("[error]")]
    print(f"{model}: {len(rs)} folds, {sum(len(v) for v in newfields.values())} new fields; changed {delta}")
    for l in errs[:6]: print("   ",l)
