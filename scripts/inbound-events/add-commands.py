#!/usr/bin/env python3
"""BACKLOG #38 item 4b, the `+` rows: an ask whose purpose no existing command
serves gets a new command on the entity, in the entity's own idiom.

    idx<TAB>+Entity.Cmd<TAB>field:Type=expr;field:Type=expr

Adds: the command (entity id field first, then the spec'd fields), its event
(same fields + recordedAt), the on-command clause (self-`tell event` or `yield`,
whichever the entity's siblings use), the on-event apply clause, membership in
the <Entity>Command and <Entity>Event alternations, a clause in the split that
fans the entity's events out (mirroring a sibling's sends, minus Persist tells),
and a no-op clause in any consumer typed with the alternation that now admits a
member it does not handle. Then forward-answers.py forwards the ask into it.
"""
import json,re,subprocess,collections,sys,os
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
def block_end(txt,start):
    """offset just past the closing brace of the block opened after `start`, then past a trailing `with { }` block, then to end of line"""
    i=txt.index("{",start); depth=0; ins=False
    j=i
    while j<len(txt):
        ch=txt[j]
        if ch=='"' and txt[j-1]!="\\": ins=not ins
        elif not ins:
            if ch=="{": depth+=1
            elif ch=="}":
                depth-=1
                if depth==0: break
        j+=1
    j+=1
    m=re.match(r"\s*with\s*\{", txt[j:])
    if m:
        k=j+m.end()-1; depth=0; ins=False
        while k<len(txt):
            ch=txt[k]
            if ch=='"' and txt[k-1]!="\\": ins=not ins
            elif not ins:
                if ch=="{": depth+=1
                elif ch=="}":
                    depth-=1
                    if depth==0: break
            k+=1
        j=k+1
    nl=txt.find("\n",j); return nl+1 if nl>=0 else len(txt)
def clause_end(txt,start):
    """offset just past the closing brace of an on-clause (no with-block handling)"""
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
def words(s): return re.sub(r"(?<!^)(?=[A-Z])"," ",s).lower()
def event_name(cmd):
    for pre,suf in (("AttributeTo","Attributed"),("Record","Recorded"),("Attach","Attached"),("Assign","Assigned")):
        if cmd.startswith(pre): return cmd[len(pre):]+suf
    return cmd+"Done"
facts=json.load(open("/tmp/ask-facts.json"))
rows={}
for l in open(sys.argv[1]):
    p=l.rstrip("\n").split("\t")
    if len(p)>=3 and p[0].isdigit() and p[1].startswith("+"): rows[int(p[0])]=(p[1][1:],p[2])
only=set(sys.argv[2:])
bym=collections.defaultdict(list)
for i,(tgt,spec) in rows.items():
    if not only or facts[i]["model"] in only: bym[facts[i]["model"]].append((i,tgt,spec))
ok=fail=0
for model,items in sorted(bym.items()):
    d=ROOT/model; c=next(d.glob("*.conf")); e=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()).group(1)
    snap={str(f.relative_to(d)):f.read_text() for f in d.glob("**/*.riddl")}
    ns=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout))); byp={n["path"]:n for n in ns if "path" in n}
    edits=collections.defaultdict(list); err=None; added=[]
    try:
        for i,tgt,spec in items:
            f=facts[i]; ent,cmd=tgt.split("."); ev=event_name(cmd)
            A=next(a for a in ns if a.get("kind")=="adaptor" and a["id"]==f["adaptor"] and byp[a["parent"]]["id"]==f["ctx"]); ctx=byp[A["parent"]]
            E=next((n for n in ns if n.get("kind")=="entity" and n["id"]==ent and n["parent"]==ctx["path"]),None)
            if not E: raise RuntimeError(f"[{i}] entity {ent} not in {ctx['id']}")
            et=snap[E["file"]]
            cmds=[n for n in ns if n.get("kind")=="command" and n.get("parent")==E["path"]]
            evs=[n for n in ns if n.get("kind")=="event" and n.get("parent")==E["path"]]
            if not cmds or not evs: raise RuntimeError(f"[{i}] {ent} has no sibling command/event to mirror")
            if any(n["id"]==cmd for n in cmds): raise RuntimeError(f"[{i}] {ent}.{cmd} already exists")
            # the entity id field, from the first sibling command
            idf=[x for x in ns if x.get("kind")=="field" and x.get("parent")==cmds[0]["path"]][0]
            idname=idf["id"]; idtype=(idf.get("type") or {}).get("ref") if isinstance(idf.get("type"),dict) else str(idf.get("type"))
            # spec fields, types qualified where they live in an external context
            fields=[]
            for part in spec.split(";"):
                nm,rest=part.split(":",1); ty,_,expr=rest.partition("=")
                base=re.match(r"[\w.]+",ty).group(0); suffix=ty[len(base):]
                if not re.match(r"^(String|Decimal|Natural|Integer|Number|Boolean|Date|DateTime|TimeStamp|Time|Duration|UUID|URL|Real)\b",base):
                    tn=[n for n in ns if n.get("kind")=="type" and n["id"]==base]
                    if not tn: raise RuntimeError(f"[{i}] type {base} not found")
                    own=byp.get(tn[0]["parent"],{})
                    if own.get("kind")=="context" and own.get("intention")=="External": ty=f"{own['id']}.{base}{suffix}"
                    elif own.get("kind")=="entity" and own["path"]!=E["path"]: ty=f"{own['id']}.{base}{suffix}"
                fields.append((nm,ty,expr))
            def fdecl(nm,ty,brief): return f"    {nm}: {ty} with {{\n      briefly \"{brief}\"\n      described as {{\n        |{brief[0].upper()+brief[1:]}.\n      }}\n    }}\n"
            # 1. command, after the last sibling command
            yields_idiom=bool(re.search(rf"command {cmds[0]['id']} yields event", et))
            cdecl=f"  command {cmd}{f' yields event {ev}' if yields_idiom else ''} is {{\n"+fdecl(idname,idtype,words(ent)+" addressed")
            for nm,ty,_ in fields: cdecl+=fdecl(nm,ty,words(nm))
            cdecl+=f"  }} with {{\n    briefly \"{words(cmd).capitalize()}\"\n    described as {{\n      |Carries an answer obtained from an external service into the {words(ent)}.\n    }}\n  }}\n"
            lastc=max(cmds,key=lambda n:n["span"]["end"]["offset"]); at=block_end(et,lastc["span"]["start"]["offset"])
            edits[E["file"]].append((at,cdecl))
            # 2. event, after the last sibling event
            edecl=f"  event {ev} is {{\n"+fdecl(idname,idtype,words(ent)+" addressed")
            for nm,ty,_ in fields: edecl+=fdecl(nm,ty,words(nm))
            edecl+=fdecl("recordedAt","TimeStamp","when it was recorded")
            edecl+=f"  }} with {{\n    briefly \"{words(ev).capitalize()}\"\n    described as {{\n      |Emitted when {words(cmd)} has been applied.\n    }}\n  }}\n"
            laste=max(evs,key=lambda n:n["span"]["end"]["offset"]); at=block_end(et,laste["span"]["start"]["offset"])
            edits[E["file"]].append((at,edecl))
            # 3. handler clauses, mirroring the sibling's
            oc=[c_ for c_ in ns if c_.get("kind")=="onmessageclause" and c_.get("path","").startswith(E["path"]+".") and (c_.get("message") or {}).get("resolved","").startswith(E["path"]+".") and byp.get((c_.get("message") or {}).get("resolved"),{}).get("kind")=="command"]
            oe=[c_ for c_ in ns if c_.get("kind")=="on-event" and c_.get("path","").startswith(E["path"]+".") and (c_.get("message") or {}).get("resolved","").startswith(E["path"]+".")]
            if not oc or not oe: raise RuntimeError(f"[{i}] {ent}: no sibling on-command/on-event clause")
            lc=max(oc,key=lambda n:n["span"]["end"]["offset"]); le=max(oe,key=lambda n:n["span"]["end"]["offset"])
            cb=cmd[0].lower()+cmd[1:]; eb=ev[0].lower()+ev[1:]
            args=", ".join([f"{idname} = {cb}.{idname}"]+[f"{nm} = {cb}.{nm}" for nm,_,_ in fields]+[f"recordedAt = prompt(\"now\")"])
            sib=et[lc["span"]["start"]["offset"]:lc["span"]["end"]["offset"]]
            emit=f"yield event {ev}({args})" if "yield event" in sib else f"tell event {ev}({args}) to entity {ctx['id']}.{ent}"
            cind=re.match(r"[ \t]*",et[et.rfind("\n",0,lc["span"]["start"]["offset"])+1:]).group(0)
            edits[E["file"]].append((clause_end(et,lc["span"]["start"]["offset"]),f"\n{cind}on {cb}: command {cmd} is {{\n{cind}  {emit}\n{cind}}}"))
            eind=re.match(r"[ \t]*",et[et.rfind("\n",0,le["span"]["start"]["offset"])+1:]).group(0)
            edits[E["file"]].append((clause_end(et,le["span"]["start"]["offset"]),f"\n{eind}on {eb}: event {ev} is {{\n{eind}  do \"apply {ev} to the {words(ent)} so it can be persisted and replayed\"\n{eind}}}"))
            # 4. alternations: the ones the entity's command inlet and event outlet carry
            for kind,member in (("inlet",f"{ent}.{cmd}"),("outlet",f"{ctx['id']}.{ent}.{ev}")):
                ports=[p for p in ns if p.get("kind")==kind and p.get("parent")==E["path"]]
                if not ports: raise RuntimeError(f"[{i}] {ent} has no {kind}")
                tn=byp.get((ports[0].get("type") or {}).get("resolved"))
                if not tn or tn.get("kind")!="type": raise RuntimeError(f"[{i}] {ent}'s {kind} is not an alternation")
                tt=snap[tn["file"]]; t0,t1=tn["span"]["start"]["offset"],tn["span"]["end"]["offset"]; tsrc=tt[t0:t1]
                sibm=re.findall(r"[\w.]+",tsrc.split("{",1)[1].split("}",1)[0]); sibm=[x for x in sibm if x!="or"]
                style=sibm[0].count("."); leaf=member.split(".")[-1]
                mem=".".join(member.split(".")[-(style+1):]) if style<member.count(".") else member
                mm=re.search(r"\n(\s*)\}", tsrc); edits[tn["file"]].append((t0+mm.start(),f" or {mem}"))
            # 5. the split's clause, mirroring a sibling event's clause
            for s in [x for x in ns if x.get("kind") in ("split","router","flow") and x.get("parent")==ctx["path"]]:
                scl=[c_ for c_ in ns if c_.get("kind")=="on-event" and c_.get("path","").startswith(s["path"]+".") and (c_.get("message") or {}).get("resolved","").startswith(E["path"]+".")]
                if not scl: continue
                st=snap[s["file"]]; sc=scl[-1]; scend=clause_end(st,sc["span"]["start"]["offset"]); body=st[sc["span"]["start"]["offset"]:scend]
                sb=sc.get("binding") if isinstance(sc.get("binding"),str) else (sc.get("binding") or {}).get("id")
                lines=[l for l in body.split("\n")[1:-1] if "Persist" not in l]
                lines=[l.replace(f" {sb} ",f" {eb} ").replace(f"({sb}.",f"({eb}.") for l in lines]
                sind=re.match(r"[ \t]*",st[st.rfind("\n",0,sc["span"]["start"]["offset"])+1:]).group(0)
                edits[s["file"]].append((scend,f"\n{sind}on {eb}: event {ent}.{ev} is {{\n"+"\n".join(lines)+f"\n{sind}}}"))
            added.append((i,ent,cmd,ev))
        for fpath,es in edits.items():
            t=snap[fpath]
            for at,s in sorted(es,key=lambda x:-x[0]): t=t[:at]+s+t[at:]
            (d/fpath).write_text(t)
        # 6. consumers now admitting a member they do not handle
        for _ in range(2):
            p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True)
            out=p.stdout+p.stderr
            fixes=re.findall(r"\[stream-inlet-not-received\] (\S+)\(\d+:\d+->\d+\):\n.*?(?:Projector|Repository|Streamlet|Sink|Flow|Split|Merge|Router) '(\w+)' declares no handler clause for \d+ of its \d+ members \(([^)]*)\)", out)
            if not fixes: break
            ns2=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout))); byp2={n["path"]:n for n in ns2 if "path" in n}
            for fl,pname,members in fixes:
                P=next((n for n in ns2 if n.get("id")==pname and n.get("kind") in ("projector","repository","split","flow","merge","router","sink")),None)
                if not P: continue
                H=[h for h in ns2 if h.get("kind")=="handler" and h.get("parent")==P["path"]]
                if not H: continue
                H=H[0]; txt=(d/H["file"]).read_text(); last=[cl for cl in ns2 if cl.get("kind") in ("on-event","onmessageclause") and cl.get("path","").startswith(H["path"]+".")]
                if not last: continue
                last=max(last,key=lambda n:n["span"]["end"]["offset"]); lend=clause_end(txt,last["span"]["start"]["offset"])
                cind=re.match(r"[ \t]*",txt[txt.rfind("\n",0,last["span"]["start"]["offset"])+1:]).group(0)
                add=""
                for en in [x.strip() for x in members.split(",")]:
                    evn=[n for n in ns2 if n.get("kind")=="event" and n["id"]==en and byp2.get(n["parent"],{}).get("kind")=="entity"]
                    if not evn: continue
                    En=byp2[evn[0]["parent"]]; b=en[0].lower()+en[1:]
                    add+=f"\n{cind}on {b}: event {En['id']}.{en} is {{\n{cind}  do \"a {words(en)} changes nothing this {P['kind']} keeps\"\n{cind}}}"
                txt=txt[:lend]+add+txt[lend:]; (d/H["file"]).write_text(txt)
        p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True)
        bad=[l for l in (p.stdout+p.stderr).splitlines() if l.strip().startswith("[error]")]
        if bad: err="\n   ".join(bad[:3])
    except Exception as ex: err=str(ex)
    if err:
        if not os.environ.get("KEEP"):
            for fpath,tx in snap.items(): (d/fpath).write_text(tx)
        print(f"REVERT {model}: {err[:300]}"); fail+=1
    else: print(f"OK     {model}: "+", ".join(f"{en}.{c_}->{ev}" for _,en,c_,ev in added)); ok+=1
print(f"\n{ok} models ok, {fail} reverted")
