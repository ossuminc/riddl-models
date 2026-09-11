#!/usr/bin/env python3
"""BACKLOG #38 items 3 and 4a: give every Missing-inlet adaptor its channel.

Under A103 an adaptor's inlet was implied and NOTHING ever fed it: the model
assumed a context routes its entity's events to its adaptors. Under [1.25]
nothing is implied, so every adaptor that handles entity events needs a real
leg from the split that fans that entity's events out, and every adaptor that
ASKS needs the reply leg riddl 8d2cc13e5 admits: a result outlet on the
answering context, a result inlet on the asker, and a connector between.

Shape handled here (669 of 731 on 2026-09-11): the adaptor handles events of
ONE entity in its OWN context, and a split in that context already handles
every event the adaptor does. Everything else is printed and left alone.

Usage: drain-inlets.py [model ...]     (default: every model with a finding)
One dump per pass; every edit by span, descending; validate-and-revert per model.
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
def shape(outs,ins):
    if outs==0 and ins==0: return "void"
    if ins==0: return "source"
    if outs==0: return "sink"
    if outs==1 and ins==1: return "flow"
    if outs>=2 and ins==1: return "split"
    if outs==1 and ins>=2: return "merge"
    return "router"
def line_start(txt,off): return txt.rfind("\n",0,off)+1
def indent_of(txt,off):
    ls=line_start(txt,off); return re.match(r"[ \t]*",txt[ls:]).group(0)
want=collections.defaultdict(set)
for l in open("/tmp/sweep47.jsonl"):
    r=json.loads(l)
    if r["rule"]=="stream-processor-no-inlet" and r["message"].startswith("Adaptor"):
        want[r["model"]].add(re.match(r"Adaptor '(\w+)'",r["message"]).group(1))
models=sys.argv[1:] or sorted(want)
ok=fail=skipped=done=0
for model in models:
    d=ROOT/model; c=next(d.glob("*.conf")); e=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()).group(1)
    snap={str(f.relative_to(d)):f.read_text() for f in d.glob("**/*.riddl")}
    ns=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout)))
    byp={n["path"]:n for n in ns if "path" in n}
    conns=[n for n in ns if n.get("kind")=="connector"]
    edits=collections.defaultdict(list)   # file -> (start,end,rep)
    hdr_delta=collections.defaultdict(lambda:[0,0])  # processor path -> [d_in,d_out]
    ext_reply=collections.defaultdict(set)  # ext ctx path -> result paths to carry
    ext_reply_to=collections.defaultdict(list)  # ext ctx path -> (adaptor path, inlet name)
    touched=0
    for aname in sorted(want.get(model,[])):
        seen=set()
        for a in [x for x in ns if x.get("kind")=="adaptor" and x["id"]==aname and not (x["path"] in seen or seen.add(x["path"]))]:
            ctx=a["parent"]; ctxn=byp[ctx]
            atxt=snap[a["file"]]; s0,s1=a["span"]["start"]["offset"],a["span"]["end"]["offset"]; ablock=atxt[s0:s1]
            evs=[c for c in ns if c.get("kind")=="on-event" and c.get("path","").startswith(a["path"]+".")]
            evp={(c.get("message") or {}).get("resolved") for c in evs}
            owners={x.rsplit(".",1)[0] for x in evp if x}
            if len(owners)!=1 or byp.get(list(owners)[0],{}).get("kind")!="entity" or byp[list(owners)[0]]["parent"]!=ctx:
                print(f"SKIP {model.split('/')[-1]}/{aname}: not own-entity ({[o.split('.')[-1] for o in owners]})"); skipped+=1; continue
            E=byp[list(owners)[0]]
            splits=[s for s in ns if s.get("kind") in ("split","router","flow") and s.get("parent")==ctx
                    and {(c.get("message") or {}).get("resolved") for c in ns if c.get("kind")=="on-event" and c.get("path","").startswith(s["path"]+".")} >= evp]
            if not splits: print(f"SKIP {model.split('/')[-1]}/{aname}: no split covers its events"); skipped+=1; continue
            S=splits[0]; sin=[p for p in ns if p.get("kind")=="inlet" and p.get("parent")==S["path"]]
            if len(sin)!=1: print(f"SKIP {model.split('/')[-1]}/{aname}: split has {len(sin)} inlets"); skipped+=1; continue
            sty=sin[0]["type"]; tyref=sty["ref"]; tykw="type" if byp.get(sty.get("resolved"),{}).get("kind")=="type" else "event"
            if tykw=="event": tyref=sty["ref"]
            # --- the adaptor's events inlet
            hm=re.match(r"adaptor \w+ (?:from|to) context [\w.]+( as \w+)? is \{[ \t]*\n", ablock); assert hm, ablock[:80]
            him=re.search(r"^(\s*)(inlet|outlet|handler) ", ablock[hm.end():], re.M); ind=him.group(1) if him else "    "
            inlet_name=f"{aname}In"
            decl=f"{ind}inlet {inlet_name} is {tykw} {tyref}\n"
            hdr_delta[a["path"]][0]+=1
            # --- the split's new leg
            stxt=snap[S["file"]]; ss=S["span"]["start"]["offset"]; sblock=stxt[ss:S["span"]["end"]["offset"]]
            newout=f"{S['id']}To{aname}"
            sfirst=next(p for p in ns if p.get("kind") in ("inlet","outlet") and p.get("parent")==S["path"])
            sind=indent_of(stxt,sfirst["span"]["start"]["offset"])
            edits[S["file"]].append((sfirst["span"]["start"]["offset"],sfirst["span"]["start"]["offset"],f"outlet {newout} is {tykw} {tyref}\n{sind}"))
            hdr_delta[S["path"]][1]+=1
            for cl in ns:
                if cl.get("kind")=="on-event" and cl.get("path","").startswith(S["path"]+".") and (cl.get("message") or {}).get("resolved") in evp:
                    b=cl.get("binding") if isinstance(cl.get("binding"),str) else (cl.get("binding") or {}).get("id")
                    body=stxt[cl["span"]["start"]["offset"]:cl["span"]["end"]["offset"]]
                    sends=list(re.finditer(r"^(\s*)send \w+ to outlet [\w.]+\n", body, re.M))
                    if not b or not sends: print(f"SKIP {model.split('/')[-1]}/{aname}: split clause without binding/send"); break
                    lm=sends[-1]; at=cl["span"]["start"]["offset"]+lm.end()
                    edits[S["file"]].append((at,at,f"{lm.group(1)}send {b} to outlet {newout}\n"))
            else:
                # connector: placed before the connector that feeds the split, in that file
                feed=[c for c in conns if (c.get("to") or {}).get("resolved")==sin[0]["path"]]
                if feed:
                    C=feed[0]; cf=snap[C["file"]]; at=line_start(cf,C["span"]["start"]["offset"]); cind=indent_of(cf,C["span"]["start"]["offset"])
                else:
                    cf=snap[ctxn["file"]]; at=ctxn["span"]["end"]["offset"]-1; cind="  "; C={"file":ctxn["file"]}
                edits[C["file"]].append((at,at,f"{cind}connector '{aname} Feed' is from outlet {ctxn['id']}.{S['id']}.{newout} to inlet {ctxn['id']}.{aname}.{inlet_name} with {{\n{cind}  briefly \"The {E['id']} events {aname} translates, on their way to it\"\n{cind}}}\n"))
                # --- the reply leg, if the adaptor asks
                asks=re.findall(r"ask query ([\w.]+) of context ([\w.]+)", ablock)
                if asks:
                    results=[]; xpaths=set()
                    for q,x in asks:
                        qn=[n for n in ns if n.get("kind")=="query" and n.get("path","").endswith("."+q.split(".")[-1]) and byp.get(n["parent"],{}).get("id")==x.split(".")[-1]]
                        if not qn: print(f"SKIP-ASK {model.split('/')[-1]}/{aname}: query {q} not found"); continue
                        qn=qn[0]; rep=(qn.get("replies") or {}).get("resolved") if isinstance(qn.get("replies"),dict) else None
                        if not rep:
                            # read it from source
                            qs=snap[qn["file"]][qn["span"]["start"]["offset"]:qn["span"]["start"]["offset"]+200]
                            mm=re.search(r"replies result ([\w.]+)", qs); rep=mm and (qn["parent"]+"."+mm.group(1).split(".")[-1])
                        if not rep: print(f"SKIP-ASK {model.split('/')[-1]}/{aname}: {q} declares no replies"); continue
                        results.append(rep); xpaths.add(qn["parent"])
                    if len(xpaths)>1: print(f"SKIP-ASK {model.split('/')[-1]}/{aname}: asks more than one context")
                    elif results:
                        X=byp[list(xpaths)[0]]; rs=sorted(set(results))
                        if len(rs)==1: rty=f"result {X['id']}.{rs[0].split('.')[-1]}"; xty=f"result {rs[0].split('.')[-1]}"
                        else:
                            rty=f"type {X['id']}.{X['id']}Reply"; xty=f"type {X['id']}Reply"
                            ext_reply[X["path"]]|=set(rs)
                        rin=f"{aname}Replies"
                        decl+=f"{ind}inlet {rin} is {rty}\n"; hdr_delta[a["path"]][0]+=1
                        ext_reply_to[X["path"]].append((a,rin,xty,rs))
            if any(x[1]==-1 for x in []): pass
            edits[a["file"]].append((s0+hm.end(),s0+hm.end(),decl)); touched+=1
    # --- external contexts: reply outlet (+ alternation type) and the domain connector
    for xp,items in ext_reply_to.items():
        X=byp[xp]; xtxt=snap[X["file"]]; xs=X["span"]["start"]["offset"]; xblock=xtxt[xs:X["span"]["end"]["offset"]]
        hm=re.match(r"external context \w+( as \w+)? is \{[ \t]*\n", xblock); assert hm, xblock[:60]
        bi=re.search(r"^(\s*)(type|inlet|outlet|handler|command|event|query|result) ", xblock[hm.end():hm.end()+4000], re.M); xi=bi.group(1) if bi else "  "
        pre=""
        rs=sorted(ext_reply.get(xp,set()))
        if rs:
            pre+=f"{xi}type {X['id']}Reply is one of {{\n{xi}  {' or '.join(r.split('.')[-1] for r in rs)}\n{xi}}} with {{\n{xi}  briefly \"Everything this service answers\"\n{xi}}}\n"
            xty=f"type {X['id']}Reply"
        else: xty=items[0][2]
        if not [p for p in ns if p.get("kind")=="outlet" and p.get("parent")==xp and p["id"]==f"{X['id']}RepliesOut"]:
            pre+=f"{xi}outlet {X['id']}RepliesOut is {xty} with {{\n{xi}  briefly \"What this service answers, on its way back\"\n{xi}}}\n"
            hdr_delta[xp][1]+=1
        edits[X["file"]].append((xs+hm.end(),xs+hm.end(),pre))
        if len(items)>1: print(f"NOTE {model.split('/')[-1]}/{X['id']}: {len(items)} askers -> one outlet cannot feed two connectors"); 
        et=snap[e]; em=re.search(r"^(\s*)domain [\w.]+ is \{\n", et, re.M); di=em.group(1)+"  "
        for a,rin,_,_ in items[:1]:
            ctxn=byp[a["parent"]]
            edits[e].append((em.end(),em.end(),f"{di}persistent connector '{X['id']}Reply Stream' is from outlet {X['id']}.{X['id']}RepliesOut to inlet {ctxn['id']}.{a['id']}.{rin} with {{\n{di}  briefly \"What {X['id']} answers {ctxn['id']}\"\n{di}}}\n"))
    # --- ascriptions by new arity
    for pth,(din,dout) in hdr_delta.items():
        n=byp[pth]; t=snap[n["file"]]; s0=n["span"]["start"]["offset"]
        ins=len([p for p in ns if p.get("kind")=="inlet" and p.get("parent")==pth])+din
        outs=len([p for p in ns if p.get("kind")=="outlet" and p.get("parent")==pth])+dout
        m=re.match(r"((?:\w+ )*?(?:adaptor \w+ (?:from|to) context [\w.]+|streamlet \w+|context \w+|external context \w+))( as \w+)?( is \{)", t[s0:s0+300]); assert m, t[s0:s0+80]
        asc = f" as {shape(outs,ins)}" if (ins and outs) else ""
        edits[n["file"]].append((s0+m.start(1),s0+m.end(3),f"{m.group(1)}{asc}{m.group(3)}"))
    if not touched: continue
    for f,es in edits.items():
        t=snap[f]
        for s,t1,rep in sorted(es,key=lambda x:-x[0]): t=t[:s]+rep+t[t1:]
        (d/f).write_text(t)
    p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True)
    bad=[l for l in (p.stdout+p.stderr).splitlines() if l.strip().startswith("[error]")]
    if bad:
        if not os.environ.get("KEEP"):
            for f,tx in snap.items(): (d/f).write_text(tx)
        print(f"REVERT {model}: {bad[0][:150]}"); fail+=1
    else: print(f"OK     {model} ({touched})"); ok+=1; done+=touched
print(f"\n{ok} models ok, {fail} reverted, {done} adaptors wired, {skipped} skipped")
