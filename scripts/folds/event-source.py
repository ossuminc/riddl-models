#!/usr/bin/env python3
"""Make a state-machine entity event-sourced, under riddl's four rules.

    ./scripts/folds/event-source.py <model-dir> <Entity> [--dry]

What it does, in the entity's file (and, for event constructors, the model):
 1. adds the `event-sourced` intention (sorted before `entity`, after `aggregate`)
 2. in every `on command` clause: a self-`tell event E(…) to entity X` becomes
    `yield event E(…)` (tell-shape ruling); the command's type gets `yields
    event E` if it lacks it
 3. every `morph` / `set state` / `set field` / `become` in an `on command`
    clause moves into the `on event E` fold of the event that clause yields,
    with `<cmd>.f` rewritten to `<ev>.f`. Where E lacks f, E GAINS f (typed
    from the command) and the clause's yield passes it; a constructor of E
    anywhere else in the model passes `f = prompt(…)`. The fold's prose goes.
    A missing fold is created after the last one in the same handler.
 4. every state's `on init { set state S to "…" }` becomes the let/yield of
    the event whose fold morphs into S (the corpus's creation idiom)
Then validates and prints the finding counts.
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
def paren_end(txt,i):
    """i at '(' -> index just past the matching ')'"""
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
def entry(d):
    for c in d.glob("*.conf"):
        m=re.search(r'input-file\s*=\s*"([^"]+)"',c.read_text())
        if m: return m.group(1)
def words(s): return re.sub(r"(?<!^)(?=[A-Z])"," ",s).lower()
def lc(s): return s[0].lower()+s[1:]
def statements(body):
    """top-level statement lines of a clause body (between the braces), with their offsets"""
    out=[]; i=body.index("{")+1; end=body.rindex("}")
    flat=re.sub(r'"(?:[^"\\]|\\.)*"',lambda m:'"'+" "*(len(m.group(0))-2)+'"',body,flags=re.S)
    for m in re.finditer(r"^[ \t]*(\S.*)$",flat[i:end],re.M):
        out.append((i+m.start(),i+m.end(),body[i+m.start():i+m.end()]))
    return out
def findings(d,e):
    p=subprocess.run([R,"--no-ansi-messages","--provide-tips","validate",e],cwd=d,capture_output=True,text=True)
    out=p.stdout+p.stderr
    return collections.Counter(re.findall(r"^\[(\w+)\] \[([\w-]+)\]",out,re.M)), out
def main():
    d=ROOT/sys.argv[1]; ent_id=sys.argv[2]; dry="--dry" in sys.argv; e=entry(d)
    before,_=findings(d,e)
    dump=json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout)
    ns=list(nodes(dump)); byp={n["path"]:n for n in ns if "path" in n}
    ent=next(n for n in ns if n["kind"]=="entity" and n["id"]==ent_id)
    fp=((d/e).parent/ent["file"]).resolve(); t=fp.read_text()
    fields={}
    for n in ns:
        if n["kind"]=="field": fields.setdefault(n["parent"],[]).append(n)
    events={n["id"]:n for n in ns if n["kind"]=="event" and n["parent"]==ent["path"]}
    commands={n["id"]:n for n in ns if n["kind"]=="command" and n["parent"]==ent["path"]}
    states=[n for n in ns if n["kind"]=="state" and n["parent"]==ent["path"]]
    inent=lambda n: ent["path"] in n.get("ancestors",[])
    cmd_clauses=[n for n in ns if n["kind"]=="onmessageclause" and inent(n) and byp.get(n["message"]["resolved"],{}).get("kind")=="command"]
    ev_clauses=[n for n in ns if n["kind"]=="on-event" and inent(n)]
    init_clauses=[n for n in ns if n["kind"]=="on-init" and inent(n)]
    edits=[]            # (start,end,new) in t
    model_edits=collections.defaultdict(list)   # other files
    new_ev_fields=collections.defaultdict(list) # event id -> [(f,type)]
    fold_bodies=collections.defaultdict(list)   # event id -> [stmt lines]
    enters={}           # state id -> event id (from morph targets)
    yields_needed={}    # command id -> event id
    log=[]
    # ---- 2+3: command clauses
    for cl in cmd_clauses:
        if ((d/e).parent/cl["file"]).resolve()!=fp: log.append(f"SKIP clause outside entity file: {cl['path']}"); continue
        s=cl["span"]["start"]["offset"]; s=t.rfind("\n",0,s)+1; en=brace_end(t,s); body=t[s:en]
        cmd=byp[cl["message"]["resolved"]]; cb=cl.get("binding") or lc(cmd["id"])
        stmts=statements(body)
        # which event does it produce?
        ev=None; yield_stmt=None; conv=[]
        for (a,b,line) in stmts:
            m=re.match(r"\s*(yield|send|tell) event ([\w.]+)\(",line) or re.match(r"\s*(yield|send|tell) event ([\w.]+)\s",line)
            if m:
                name=m.group(2).split(".")[-1]
                if name in events:
                    if m.group(1)=="tell" and re.search(r"to entity [\w.]*"+re.escape(ent_id)+r"(?: by \w+)?\s*$",line):
                        conv.append((a,b,re.sub(r"^(\s*)tell event",r"\1yield event",re.sub(r"\s*to entity [\w.]*"+re.escape(ent_id)+r"(?: by \w+)?\s*$","",line))))
                        ev=ev or name; yield_stmt=(a,b)
                    elif m.group(1)=="yield": ev=ev or name; yield_stmt=(a,b)
                    elif m.group(1)=="send" and ev is None: ev=name; yield_stmt=None
            m2=re.match(r"\s*yield (\w+)\s*$",line)
            if m2:
                # let-bound: find `let x: type E`
                ml=re.search(r"let "+re.escape(m2.group(1))+r": type ([\w.]+)",body)
                if ml: ev=ev or ml.group(1).split(".")[-1]
        muts=[(a,b,line) for (a,b,line) in stmts if re.match(r"\s*(morph |set state |set field |become )",line)]
        # a `let` the mutations use (`with x`, `to x`) moves with them
        used=set()
        for (_,_,line) in muts:
            for mm in re.finditer(r"\b(?:with|to) (\w+)\s*$",line): used.add(mm.group(1))
        lets=[(a,b,line) for (a,b,line) in stmts if re.match(r"\s*let (\w+)",line) and re.match(r"\s*let (\w+)",line).group(1) in used]
        muts=sorted(lets+muts)
        if ev is None:
            if muts: log.append(f"NO EVENT for {cmd['id']}: {len(muts)} mutations left in place")
            continue
        # send-only: the clause must also yield what the command declares
        if yield_stmt is None and not conv:
            for (a,b,line) in stmts:
                ms=re.match(r"(\s*)send event ([\w.]*"+re.escape(ev)+r")\((.*)\) to outlet .*$",line)
                if ms:
                    edits.append((s+a,s+a,f"{ms.group(1)}yield event {ev}({ms.group(3)})\n")); yield_stmt=(a,b); break
        if not muts and not conv:
            fold_bodies.setdefault(ev,[]); yields_needed[cmd["id"]]=ev; continue
        evn=events[ev]; evb=lc(ev); evf={f["id"]:f for f in fields.get(evn["path"],[])}; cmdf={f["id"]:f for f in fields.get(cmd["path"],[])}
        yields_needed[cmd["id"]]=ev
        # rewrite mutations for the fold
        need=[]
        def rw(m):
            f=m.group(1)
            if f in evf: return f"{evb}.{f}"
            if f in cmdf:
                if f not in [x for x,_ in new_ev_fields[ev]]:
                    fs_=cmdf[f]["span"]; src=t[fs_["start"]["offset"]:fs_["end"]["offset"]]
                    mt=re.match(r"\s*"+re.escape(f)+r"\s*:\s*(.*?)\s*(?:with\s*\{.*)?$",src,re.S)
                    ty=mt.group(1).strip() if mt else cmdf[f]["type"].replace("type ","")
                    new_ev_fields[ev].append((f,ty)); need.append(f)
                return f"{evb}.{f}"
            return f'prompt("the {words(f)} carried by {ev}")'
        for (a,b,line) in muts:
            newline=re.sub(r"\b"+re.escape(cb)+r"\.(\w+)",rw,line)
            mm=re.search(r"morph entity [\w.]+ to state ([\w.]+)",newline)
            if mm: enters.setdefault(mm.group(1).split(".")[-1],ev)
            fold_bodies[ev].append(newline.strip())
        # edits in the command clause: remove mutations, convert self-tells, pass new fields in the yield
        for (a,b,line) in muts:
            nl=b+1 if t[s+b:s+b+1]=="\n" else b
            edits.append((s+a,s+nl,""))
        for (a,b,new) in conv: edits.append((s+a,s+b,new))
        if need:
            # the yield/tell constructor in this clause
            ys=yield_stmt
            if ys is None:
                # the send constructor is the only one; the fold cannot get its fields, so pass them there
                for (a,b,line) in stmts:
                    if re.match(r"\s*send event [\w.]*"+re.escape(ev)+r"\(",line): ys=(a,b); break
            if ys is None: log.append(f"NO CONSTRUCTOR of {ev} in {cmd['id']} clause for new fields {need}")
            else:
                a,b=ys; seg=t[s+a:s+b]; i=seg.index("("); j=paren_end(seg,i)
                inner=seg[i+1:j-1].strip()
                add=", ".join(f"{f} = {cb}.{f}" for f in need)
                newseg=seg[:i+1]+inner+(", " if inner else "")+add+seg[j-1:]
                # if a conv edit covers the same span, fold the addition into it
                done=False
                for k,(ca,cb_,cnew) in enumerate(edits):
                    if (ca,cb_)==(s+a,s+b):
                        ci=cnew.index("("); cj=paren_end(cnew,ci); cinner=cnew[ci+1:cj-1].strip()
                        edits[k]=(ca,cb_,cnew[:ci+1]+cinner+(", " if cinner else "")+add+cnew[cj-1:]); done=True
                if not done: edits.append((s+a,s+b,newseg))
    # yields on command types
    for cid,ev in yields_needed.items():
        cmd=commands[cid]
        if "yields event" in cmd.get("type",""): continue
        s=cmd["span"]["start"]["offset"]
        m=re.compile(r"command "+re.escape(cid)+r"\s+is\s*\{").search(t,s)
        if m: edits.append((m.start(),m.end(),f"command {cid} yields event {ev} is {{"))
        else: log.append(f"could not add yields to command {cid}")
    # ---- 3: folds
    by_ev={cl["message"]["resolved"].split(".")[-1]:cl for cl in ev_clauses}
    last_fold=max(ev_clauses,key=lambda c:c["span"]["start"]["offset"]) if ev_clauses else (max(cmd_clauses,key=lambda c:c["span"]["start"]["offset"]) if cmd_clauses else None)
    for ev,lines in fold_bodies.items():
        evb=lc(ev)
        if ev in by_ev:
            if not lines: continue
            cl=by_ev[ev]; s=cl["span"]["start"]["offset"]; s=t.rfind("\n",0,s)+1; en=brace_end(t,s); body=t[s:en]
            indent=re.match(r"\s*",body).group(0)
            head=re.match(r"\s*on (?:(\w+): )?event ([\w.]+) is",body); b=head.group(1) or evb
            lines2=[re.sub(r"\b"+re.escape(evb)+r"\.",b+".",l) for l in lines]
            keep=[l for (_,_,l) in statements(body) if not re.match(r'\s*(do |set \S+ to prompt\()',l)]
            new=f"{indent}on {b}: event {ev} is {{\n"+"\n".join(indent+"  "+l for l in lines2+[k.strip() for k in keep])+f"\n{indent}}}"
            edits.append((s,en,new))
        else:
            if last_fold is None: log.append(f"no fold and no handler position for {ev}"); continue
            s=last_fold["span"]["start"]["offset"]; s=t.rfind("\n",0,s)+1; en=brace_end(t,s); indent=re.match(r"\s*",t[s:]).group(0)
            if not lines: lines=[f'do "apply {ev} to the {words(ent_id)}"']
            new=f"\n{indent}on {evb}: event {ev} is {{\n"+"\n".join(indent+"  "+l for l in lines)+f"\n{indent}}}"
            edits.append((en,en,new))
    # ---- 3b: new event fields, and other constructors of E in the model
    for ev,fs in new_ev_fields.items():
        evn=events[ev]; s=evn["span"]["start"]["offset"]; en=brace_end(t,s); ins=t.rfind("\n",s,en)+1
        decl="".join(f'    {f}: {ty} with {{\n      briefly "{words(f).capitalize()}"\n    }}\n' for f,ty in fs)
        edits.append((ins,ins,decl))
        for rf in d.rglob("*.riddl"):
            rt=rf.read_text() if rf.resolve()!=fp else t
            for m in re.finditer(r"\b"+re.escape(ev)+r"\(",rt):
                # skip the constructors this script already extended (in the entity file, inside command clauses)
                if rf.resolve()==fp and any(a<=m.start()<b for (a,b,_) in edits if _!="" ): continue
                j=paren_end(rt,m.end()-1); inner=rt[m.end():j-1].strip()
                if all(re.search(r"\b"+f+r"\s*=",inner) for f,_ in fs): continue
                add=", ".join(f'{f} = prompt("the {words(f)} of this {words(ev)}")' for f,_ in fs if not re.search(r"\b"+f+r"\s*=",inner))
                tgt=edits if rf.resolve()==fp else model_edits[rf]
                tgt.append((j-1,j-1,(", " if inner else "")+add))
    # ---- 4: on init
    for ic in init_clauses:
        s=ic["span"]["start"]["offset"]; s=t.rfind("\n",0,s)+1; en=brace_end(t,s); body=t[s:en]
        m=re.search(r"set state (\w+) to ",body)
        if not m: continue
        st=m.group(1); ev=enters.get(st)
        if ev is None and states and states[0]["id"]==st:
            for s2 in states[1:]:
                if s2["id"] in enters: ev=enters[s2["id"]]; log.append(f"on init of initial {st}: yields the creation event {ev}"); break
        if ev is None:
            # an existing fold that morphs into it (already event-sourced style)?
            mm=re.search(r"to state [\w.]*\."+st+r" with",t)
            log.append(f"on init of {st}: no event morphs into it; left as is"); continue
        indent=re.match(r"\s*",body).group(0); evb=lc(ev)
        new=f'{indent}on init is {{\n{indent}  let {evb}: type {ev} = prompt("the {words(ev)} that brings this {words(ent_id)} into existence")\n{indent}  yield {evb}\n{indent}}}'
        edits.append((s,en,new))
    # ---- 1: intention
    s=ent["span"]["start"]["offset"]; m=re.compile(r"((?:aggregate )?)entity "+re.escape(ent_id)).search(t,s)
    edits.append((m.start(),m.end(),f"{m.group(1)}event-sourced entity {ent_id}"))
    for l in log: print("  ",l)
    if dry:
        print(f"{sys.argv[1]} {ent_id}: {len(edits)} edits, folds for {sorted(fold_bodies)}, new event fields {dict(new_ev_fields)}, inits {enters}"); return
    for a,b,new in sorted(edits,key=lambda x:(x[0],x[1]),reverse=True): t=t[:a]+new+t[b:]
    fp.write_text(t)
    for rf,es in model_edits.items():
        rt=rf.read_text()
        for a,b,new in sorted(es,reverse=True): rt=rt[:a]+new+rt[b:]
        rf.write_text(rt)
    after,out=findings(d,e)
    delta={k:(before.get(k,0),after.get(k,0)) for k in set(before)|set(after) if before.get(k,0)!=after.get(k,0)}
    print(f"{sys.argv[1]} {ent_id}: {len(fold_bodies)} folds, new event fields {sum(len(v) for v in new_ev_fields.values())}, inits {len(enters)}; changed {delta}")
    for l in [l for l in out.splitlines() if l.startswith("[error]")][:8]: print("   ",l)
main()
