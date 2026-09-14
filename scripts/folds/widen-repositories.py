#!/usr/bin/env python3
"""riddl-generator's 2026-09-12 task: reactive-bbq's repository clauses describe
rows (in `do` prose) that their Persist commands and Stored records cannot
hold. Option 1, widen the types to what the prose says:

  insert row into S.T with a, b, c        -> Persist<E> carries a, b, c (typed
                                             from event E); Stored<X> declares
                                             them
  update S.T set col = evf, …             -> Persist<E> carries evf; Stored<X>
                                             declares col (optional)
  update S.T set a, b                     -> col = evf = a
  update S.T set status = Literal         -> Stored<X> declares status typed as
                                             the entity state's field
  update S.T with a and b                 -> as `set a, b`
  append x to coll … / remove X with k    -> Persist<E> carries x / k; Stored<X>
                                             declares coll as a collection
The projector's `Persist<E>(id = ev.id)` constructor passes every new field
from the event, or a prompt when the event does not carry it. The prose is
left as written: it is the row riddlg fills, and it now agrees with the types.
    ./scripts/folds/widen-repositories.py [--dry]
"""
import json,re,subprocess,sys,collections
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
D=ROOT/"hospitality/food-service/reactive-bbq"; E="reactive-bbq.riddl"
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
dry="--dry" in sys.argv
d=json.loads(subprocess.run([R,"dump",E,"--json"],cwd=D,capture_output=True,text=True).stdout)
ns=list(nodes(d)); byp={n["path"]:n for n in ns if "path" in n}
texts={}
def text(f):
    fp=(D/f).resolve()
    if fp not in texts: texts[fp]=fp.read_text()
    return fp
fields=collections.defaultdict(list)
for n in ns:
    if n["kind"]=="field": fields[n["parent"]].append(n)
def src_type(fn):
    fp=text(fn["file"]); t=texts[fp]; s=fn["span"]; src=t[s["start"]["offset"]:s["end"]["offset"]]
    m=re.match(r"\s*"+re.escape(fn["id"])+r"\s*:\s*(.*?)\s*(?:with\s*\{.*)?$",src,re.S)
    return (m.group(1).strip() if m else fn["type"].replace("type ","")).rstrip()
events={n["id"]:n for n in ns if n["kind"]=="event"}
entities={n["id"]:n for n in ns if n["kind"]=="entity"}
edits=collections.defaultdict(list)   # fp -> [(start,end,new)]
report=[]
for repo in [n for n in ns if n["kind"]=="repository"]:
    schema=next((n for n in ns if n["kind"]=="schema" and n["parent"]==repo["path"]),None)
    if not schema: report.append(f"{repo['id']}: no schema, skipped"); continue
    fps=text(schema["file"]); ms=re.search(r"as record (\S+)",texts[fps][schema["span"]["start"]["offset"]:brace_end(texts[fps],schema["span"]["start"]["offset"]) if "{" in texts[fps][schema["span"]["start"]["offset"]:schema["span"]["end"]["offset"]] else schema["span"]["end"]["offset"]])
    stored=next((n for n in ns if n["kind"]=="record" and n["id"]==ms.group(1).split(".")[-1]),None) if ms else None
    if not stored: report.append(f"{repo['id']}: schema names no record, skipped"); continue
    scols={f["id"]:f for f in fields[stored["path"]]}
    ent=next((e for e in entities.values() if e["id"]==stored["id"][6:]),None) or next((e for e in entities.values() if e["id"] in stored["id"]),None)
    state_fields={}
    if ent:
        for st in [n for n in ns if n["kind"]=="state" and n["parent"]==ent["path"]]:
            fp=text(st["file"]); mm=re.match(r"\s*(?:initial )?state \S+ of (?:record )?(\S+)",texts[fp][st["span"]["start"]["offset"]:])
            if mm:
                rec=next((n for n in ns if n["kind"]=="record" and n["id"]==mm.group(1).split(".")[-1]),None)
                if rec:
                    for f in fields[rec["path"]]: state_fields.setdefault(f["id"],f)
    new_scols={}   # name -> type
    new_cfields=collections.defaultdict(dict)  # command path -> {name: (type, source event field or None)}
    for cl in [n for n in ns if n["kind"]=="onmessageclause" and repo["path"] in n.get("ancestors",[])]:
        cmd=byp.get(cl["message"]["resolved"])
        if not cmd or cmd["kind"]!="command" or not cmd["id"].startswith("Persist"): continue
        fp=text(cl["file"]); t=texts[fp]; s=cl["span"]["start"]["offset"]; body=t[s:brace_end(t,s)]
        m=re.search(r'do "(.*?)"',body,re.S)
        if not m: continue
        prose=" ".join(m.group(1).split())
        evn=events.get(cmd["id"][7:])
        evf={f["id"]:f for f in fields[evn["path"]]} if evn else {}
        cf={f["id"]:f for f in fields[cmd["path"]]}
        idf=next(iter(cf)) if cf else None
        ops=[]   # (col, src, mode)  src: event field name | ("lit",value) | None
        if prose.startswith("insert"):
            mm=re.search(r"with (.*)$",prose)
            for tok in re.split(r",?\s+and\s+|,\s*",mm.group(1)) if mm else []:
                tok=tok.strip().rstrip(".")
                if not tok: continue
                if "=" in tok:
                    a,b=[x.strip() for x in tok.split("=",1)]; ops.append((a,b if b in evf else ("lit",b),"insert"))
                else: ops.append((tok,tok,"insert"))
        mn=re.search(r"(\w+)\[(\w+)\]\.(\w+)\s*=",prose)
        if mn:
            coll,key=mn.group(1),mn.group(2)
            if key in evf and key not in cf: new_cfields[cmd["path"]][key]=(src_type(evf[key]),key)
            if coll not in scols and coll not in new_scols:
                sf=state_fields.get(coll)
                if sf: new_scols[coll]=src_type(sf)
        if mn: pass
        elif prose.startswith("update") or prose.startswith("set"):
            mm=re.search(r"(?:set|with) (.*?)(?: where .*)?$",prose)
            if mm:
                for tok in re.split(r",?\s+and\s+|,\s*",mm.group(1)):
                    tok=tok.strip()
                    if not tok or tok=="where": continue
                    if "=" in tok:
                        a,b=[x.strip() for x in tok.split("=",1)]; ops.append((a,b if b in evf else ("lit",b),"update"))
                    elif re.match(r"^[a-z]\w*$",tok): ops.append((tok,tok,"update"))
        elif prose.startswith("append"):
            mm=re.match(r"append (\w+)(?: \w+)? to (\w+)",prose)
            if mm: ops.append((mm.group(2),mm.group(1),"append"))
        elif prose.startswith("remove"):
            mm=re.match(r"remove \w+ with (\w+) from (\w+)",prose)
            if mm: ops.append((mm.group(2),mm.group(1),"remove"))
        prose_new=m.group(1)
        # `col = a + b`: an expression -- every event field it names rides on the command
        for col,src,mode in list(ops):
            if isinstance(src,tuple) and re.search(r"[+\-*/]",src[1]):
                for tok in re.findall(r"\b[a-z]\w*\b",src[1]):
                    if tok in evf and tok not in cf and tok not in new_cfields[cmd["path"]]: new_cfields[cmd["path"]][tok]=(src_type(evf[tok]),tok)
        for col,src,mode in ops:
            if col==idf: continue
            # the source: an event field the command must carry
            if isinstance(src,tuple):
                # literal: the stored column takes the entity state's type for that column
                if col not in scols and col not in new_scols:
                    sf=state_fields.get(col)
                    if sf: new_scols[col]=src_type(sf)
                    else: report.append(f"{repo['id']}.{cmd['id']}: literal for {col}, no state field to type it")
                continue
            if src in evf:
                ty=src_type(evf[src]); base=re.sub(r"[?*+]$","",ty)
                if src not in cf and src not in new_cfields[cmd["path"]]: new_cfields[cmd["path"]][src]=(ty,src)
                if mode in("append","remove"):
                    if col not in scols and col not in new_scols: new_scols[col]=base+"*"
                    continue
                if col not in scols and col not in new_scols:
                    if mode=="insert": new_scols[col]=ty
                    else:
                        opt=ty if ty.endswith(("?","*")) else ty+"?"
                        if col==src and opt!=ty:
                            newcol="actual"+col[0].upper()+col[1:]
                            new_scols[newcol]=opt
                            # the prose must name the column it writes; one rewrite per clause, applied below
                            pat=re.compile(r"(?<![\w.])"+re.escape(col)+r"\s*=\s*"+re.escape(col)+r"(?![\w])",re.S)
                            if pat.search(prose_new): prose_new=pat.sub(f"{newcol} = {col}",prose_new,count=1)
                            else: prose_new=re.sub(r"(?<![\w.=])"+re.escape(col)+r"(?![\w=])",f"{newcol} = {col}",prose_new,count=1)
                            report.append(f"{repo['id']}.{cmd['id']}: column {col} declared as `{newcol}` (optional), prose updated")
                        else: new_scols[col]=opt
            elif any(True for ef in evf.values() for rec in [next((n for n in ns if n["kind"]=="record" and n["id"]==re.sub(r"[?*+]$","",src_type(ef))),None)] if rec and src in {f["id"] for f in fields[rec["path"]]}):
                ef=next(ef for ef in evf.values() for rec in [next((n for n in ns if n["kind"]=="record" and n["id"]==re.sub(r"[?*+]$","",src_type(ef))),None)] if rec and src in {f["id"] for f in fields[rec["path"]]})
                rec=next(n for n in ns if n["kind"]=="record" and n["id"]==re.sub(r"[?*+]$","",src_type(ef)))
                nf=next(f for f in fields[rec["path"]] if f["id"]==src); ty=src_type(nf)
                if src not in cf and src not in new_cfields[cmd["path"]]: new_cfields[cmd["path"]][src]=(ty,f"{ef['id']}.{src}")
                if col not in scols and col not in new_scols: new_scols[col]=ty if mode=="insert" or ty.endswith(("?","*")) else ty+"?"
            else:
                sf=state_fields.get(src)
                if sf:
                    ty=src_type(sf); base=re.sub(r"[?*+]$","",ty)
                    if src not in cf and src not in new_cfields[cmd["path"]]: new_cfields[cmd["path"]][src]=(ty,None)
                    if col not in scols and col not in new_scols: new_scols[col]=(base+"*") if mode in("append","remove") else (ty if mode=="insert" or ty.endswith(("?","*")) else ty+"?")
                else: report.append(f"{repo['id']}.{cmd['id']}: `{src}` is neither an event field nor a state field; skipped")
        if prose_new!=m.group(1): edits[fp].append((s+m.start(1),s+m.end(1),prose_new))
    # ---- emit
    fp=text(stored["file"]); t=texts[fp]
    if new_scols:
        s=stored["span"]["start"]["offset"]; en=brace_end(t,s); ins=t.rfind("\n",s,en)+1
        decl="".join(f'      {c}: {ty} with {{\n        briefly "{words(c).capitalize()}"\n      }}\n' for c,ty in new_scols.items())
        edits[fp].append((ins,ins,decl))
    for cp,fs in new_cfields.items():
        cmd=byp[cp]; fp2=text(cmd["file"]); t2=texts[fp2]; s=cmd["span"]["start"]["offset"]; en=brace_end(t2,s); ins=t2.rfind("\n",s,en)+1
        decl="".join(f'      {f}: {ty} with {{\n        briefly "{words(f).capitalize()}"\n      }}\n' for f,(ty,_) in fs.items())
        edits[fp2].append((ins,ins,decl))
        # every constructor of the command in the model
        for rf in D.rglob("*.riddl"):
            rfp=text(str(rf.relative_to(D))); rt=texts[rfp]
            for m in re.finditer(r"\b"+re.escape(cmd["id"])+r"\(",rt):
                j=paren_end(rt,m.end()-1); inner=rt[m.end():j-1]
                mb=re.search(r"=\s*(\w+)\.\w+",inner); evb=mb.group(1) if mb else None
                add=[]
                for f,(ty,srcf) in fs.items():
                    if re.search(r"\b"+f+r"\s*=",inner): continue
                    add.append(f"{f} = {evb}.{srcf}" if (srcf and evb) else f'{f} = prompt("the {words(f)} of this row")')
                if add: edits[rfp].append((j-1,j-1,(", " if inner.strip() else "")+", ".join(add)))
    report.append(f"{repo['id']}: +{len(new_scols)} columns, +{sum(len(v) for v in new_cfields.values())} command fields")
for l in report: print("  ",l)
if dry: sys.exit(0)
for fp,es in edits.items():
    t=texts[fp]
    for s,en,new in sorted(es,key=lambda x:x[0],reverse=True): t=t[:s]+new+t[en:]
    fp.write_text(t)
p=subprocess.run([R,"--no-ansi-messages","--provide-tips","validate",E],cwd=D,capture_output=True,text=True); out=p.stdout+p.stderr
print(collections.Counter(re.findall(r"^\[(\w+)\] \[([\w-]+)\]",out,re.M)))
for l in [l for l in out.splitlines() if l.startswith("[error]")][:10]: print("   ",l)
