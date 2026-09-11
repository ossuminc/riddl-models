#!/usr/bin/env python3
"""Inbound placeholders -> a real channel. One ORDERED pass per model.

Every edit inside a file is applied in DESCENDING span order from a single dump,
so an earlier insertion can never shift a later site's offsets. The first version
re-dumped per external context and silently lost two adaptor inlets out of four.

Reid's rulings (2026-09-10):
  * the external system FIRES these events; we model the PATH, not the emission,
    for a context that declares only events
  * where the event acknowledges a command we send or a query we ask, the
    emission hangs off OUR handler for it -- a fact the model does own
  * what the clause DOES is per-case by the counterparty test

Two shapes, and which one applies depends on what the clause does:
  PROSE  the adaptor is the chain TAIL, so it must DECLARE an inlet --
         `isStreamTail` opens `if proc.inlets.isEmpty then false` over DECLARED
         ports, and A103's implied inlet is not one of them
  TELL   the adaptor is a MIDDLE node: it needs a declared outlet, our context
         needs its own inlet for it, and a connector must join them. This is the
         shape order-management's PaymentAdapter already uses.

Input:  model|Ctx.Event|cause|action|payload
"""
import json, re, subprocess, sys, collections, os
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"

def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)

def entry_of(d):
    for c in d.glob("*.conf"):
        m=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text())
        return d/(m.group(1) if m else f"{d.name}.riddl")

def dump(d,e):
    p=subprocess.run([R,"dump",e.name,"--json"],cwd=d,capture_output=True,text=True)
    return list(nodes(json.loads(p.stdout)))

def shape_for(outs,ins):
    if outs==0 and ins==0: return "void"
    if ins==0:  return "source"
    if outs==0: return "sink"
    if outs==1 and ins==1: return "flow"
    if outs>=2 and ins==1: return "split"
    if outs==1 and ins>=2: return "merge"
    return "router"

def apply_edits(d, edits):
    """edits: list of (file, start, end, replacement) -- applied per file, descending."""
    byf=collections.defaultdict(list)
    for f,s,t,rep in edits: byf[f].append((s,t,rep))
    for f,es in byf.items():
        txt=(d/f).read_text()
        for s,t,rep in sorted(es, key=lambda x:-x[0]):
            txt=txt[:s]+rep+txt[t:]
        (d/f).write_text(txt)

rows=[l.rstrip("\n").split("|") for l in open(sys.argv[1]) if l.strip()]
bym=collections.defaultdict(list)
for r in rows: bym[r[0]].append(r)
ok=fail=0
for model, rs in sorted(bym.items()):
    d=ROOT/model; e=entry_of(d)
    files={f.name for f in d.glob("*.riddl")}
    snap={f:(d/f).read_text() for f in files}
    err=None
    byctx=collections.defaultdict(list)
    for r in rs: byctx[r[1].rsplit(".",1)[0]].append(r)
    try:
        # ---------- PASS 1: the external contexts' event surface ----------
        ns=dump(d,e)
        edits=[]; plan={}
        for ctx, crs in byctx.items():
            cnode=next((n for n in ns if n.get("kind")=="context" and n.get("id")==ctx
                        and n.get("intention")=="External"), None)
            if not cnode: raise RuntimeError(f"{ctx}: external context not found")
            cp=cnode["path"]
            ad=next((a for a in ns if a.get("kind")=="adaptor" and a.get("id")==f"From{ctx}"), None)
            if not ad: raise RuntimeError(f"{ctx}: no adaptor From{ctx}")
            if [n for n in ns if n.get("kind")=="outlet" and n.get("parent")==cp]:
                raise RuntimeError(f"{ctx}: already has an outlet")
            # Only 2 of the 597 From adaptors in play already declare a port.
            # Refuse those rather than guess how to merge with existing wiring --
            # the outbound campaign's merge path corrupted four models before it
            # was removed in favour of exactly this refusal.
            if [n for n in ns if n.get("kind") in ("inlet","outlet")
                and n.get("parent")==ad["path"]]:
                raise RuntimeError(f"From{ctx}: already declares a port -- do this one by hand")
            pins=[n for n in ns if n.get("kind")=="inlet" and n.get("parent")==cp]
            evs=[r[1].rsplit(".",1)[1] for r in crs]
            tells=[r for r in crs if r[3]=="tell"]
            plan[ctx]=dict(cp=cp, adpath=ad["path"], owner=ad["path"].rsplit(".",1)[0],
                           ocid=ad["path"].rsplit(".",2)[-2], evs=evs, tells=tells,
                           multi=len(evs)>1, rows=crs)
            txt=(d/cnode["file"]).read_text()
            s0=cnode["span"]["start"]["offset"]
            hm=re.match(rf"external context {ctx}( as \w+)? is \{{[ \t]*\n",
                        txt[s0:cnode["span"]["end"]["offset"]])
            if not hm: raise RuntimeError(f"{ctx}: declaration header")
            bi=re.search(r"^(\s*)(type|inlet|outlet|handler|command|event|query|result) ",
                         txt[s0+hm.end():s0+hm.end()+4000], re.M)
            i2=bi.group(1) if bi else "  "
            ety = f"type {ctx}Event" if len(evs)>1 else f"event {evs[0]}"
            pre=""
            if len(evs)>1:
                pre=(f"{i2}type {ctx}Event is one of {{\n{i2}  {' or '.join(evs)}\n{i2}}} with {{\n"
                     f'{i2}  briefly "Everything this service tells the model, unasked"\n{i2}}}\n')
            shp=shape_for(1, len(pins))
            rep=(f"external context {ctx} as {shp} is {{\n"+pre
                 + f"{i2}outlet {ctx}EventsOut is {ety} with {{\n"
                 + f'{i2}  briefly "What this service tells the model, unasked"\n{i2}}}\n')
            edits.append((cnode["file"], s0, s0+hm.end(), rep))
            plan[ctx]["aty"]=f"type {ctx}.{ctx}Event" if len(evs)>1 else f"event {ctx}.{evs[0]}"
        apply_edits(d, edits)

        # ---------- PASS 2: emission, only where one of OUR messages causes it ----------
        ns=dump(d,e); edits=[]
        for ctx,pl in plan.items():
            cnode=next(n for n in ns if n.get("kind")=="context" and n.get("id")==ctx
                       and n.get("intention")=="External")
            txt=(d/cnode["file"]).read_text()
            s0,s1=cnode["span"]["start"]["offset"], cnode["span"]["end"]["offset"]
            body=txt[s0:s1]
            for _, ctxev, cause, _, _ in pl["rows"]:
                if cause=="-": continue
                ev=ctxev.rsplit(".",1)[1]
                cm=re.search(rf"^(\s*)on (?:\w+: )?(command|query) {re.escape(cause)} is \{{\n",
                             body, re.M)
                if not cm: raise RuntimeError(f"{ev}: no handler clause for {cause}")
                j=cm.group(1)+"  "
                b=ev[0].lower()+ev[1:]
                words=re.sub(r"(?<!^)(?=[A-Z])"," ",ev).lower()
                ins=(f'{j}let {b}: type {ev} = prompt("the {words} this produces")\n'
                     f"{j}send {b} to outlet {ctx}.{ctx}EventsOut\n")
                edits.append((cnode["file"], s0+cm.end(), s0+cm.end(), ins))
        apply_edits(d, edits)

        # ---------- PASS 3: the adaptors' ports ----------
        ns=dump(d,e); edits=[]
        for ctx,pl in plan.items():
            ad=next(a for a in ns if a.get("kind")=="adaptor" and a["path"]==pl["adpath"])
            txt=(d/ad["file"]).read_text()
            s0,s1=ad["span"]["start"]["offset"], ad["span"]["end"]["offset"]
            block=txt[s0:s1]
            hm=re.match(rf"adaptor From{ctx} from context ([\w.]+)( as \w+)? is \{{[ \t]*\n", block)
            if not hm: raise RuntimeError(f"{ctx}: adaptor header")
            him=re.search(r"^(\s*)handler ", block, re.M)
            ai=him.group(1) if him else "    "
            ports=f"{ai}inlet From{ctx}In is {pl['aty']}\n"
            if pl["tells"]:
                cmds=sorted({r[4].split("::",1)[0] for r in pl["tells"]})
                pl["cmds"]=cmds
                oty=f"command {cmds[0]}" if len(cmds)==1 else f"type {pl['ocid']}.From{ctx}Command"
                pl["oty"]=oty
                ports+=f"{ai}outlet From{ctx}To{pl['ocid']} is {oty}\n"
            # [1.25]: ascribe by DECLARED arity. A prose-only From adaptor has an inlet
            # and no transmission; Reid ruled it must not be written `as sink`, so it
            # carries no ascription until an outlet is authored.
            asc=" as flow" if pl["tells"] else ""
            rep=f"adaptor From{ctx} from context {hm.group(1)}{asc} is {{\n"+ports
            edits.append((ad["file"], s0, s0+hm.end(), rep))
        apply_edits(d, edits)

        # ---------- PASS 4: what we DO about each event ----------
        ns=dump(d,e); edits=[]; taken={n.get("id") for n in ns}
        for ctx,pl in plan.items():
            ad=next(a for a in ns if a.get("kind")=="adaptor" and a["path"]==pl["adpath"])
            txt=(d/ad["file"]).read_text()
            s0,s1=ad["span"]["start"]["offset"], ad["span"]["end"]["offset"]
            block=txt[s0:s1]
            for _, ctxev, _, action, payload in pl["rows"]:
                ev=ctxev.rsplit(".",1)[1]
                ph=re.search(rf'^(\s*)on event {ctx}\.{ev} is \{{\n\s*do "the model receives[^"]*"\n\s*\}}\n',
                             block, re.M)
                if not ph: raise RuntimeError(f"{ev}: placeholder not in adaptor span")
                i=ph.group(1)
                b=ev[0].lower()+ev[1:]
                if b in taken: b+="Event"
                if action=="prose":
                    inner=f'{i}  do "{payload}"\n'
                else:
                    cmd,why=payload.split("::",1)
                    inner=(f'{i}  let item0: type {cmd} = prompt("translate the {b} event into a '
                           f'{cmd.split(".")[-1]}, {why}")\n'
                           f"{i}  send item0 to outlet {pl['owner'].split('.')[-1]}.From{ctx}.From{ctx}To{pl['ocid']}\n")
                rep=f"{i}on {b}: event {ctx}.{ev} is {{\n"+inner+f"{i}}}\n"
                edits.append((ad["file"], s0+ph.start(), s0+ph.end(), rep))
        apply_edits(d, edits)

        # ---------- PASS 5: our context's intake for telling adaptors ----------
        ns=dump(d,e); edits=[]
        telling={c:pl for c,pl in plan.items() if pl["tells"]}
        byowner=collections.defaultdict(list)
        for c,pl in telling.items(): byowner[pl["owner"]].append((c,pl))
        for owner, items in byowner.items():
            oc=next(n for n in ns if n.get("kind")=="context" and n["path"]==owner)
            txt=(d/oc["file"]).read_text()
            s0=oc["span"]["start"]["offset"]
            hm=re.match(r"((?:\w+ )*context )(\w+)( as \w+)? is \{[ \t]*\n",
                        txt[s0:oc["span"]["end"]["offset"]])
            if not hm: raise RuntimeError(f"{owner}: owner context header")
            bi=re.search(r"^(\s*)(inlet|outlet|handler|type) ", txt[s0+hm.end():s0+hm.end()+4000], re.M)
            k=bi.group(1) if bi else "  "
            nin=len([n for n in ns if n.get("kind")=="inlet"  and n.get("parent")==owner])+len(items)
            nout=len([n for n in ns if n.get("kind")=="outlet" and n.get("parent")==owner])
            pre=""
            for ctx,pl in items:
                if len(pl["cmds"])>1:
                    pre+=(f"{k}type From{ctx}Command is one of {{\n{k}  {' or '.join(pl['cmds'])}\n"
                          f"{k}}} with {{\n{k}  briefly \"What From{ctx} turns that service's news into\"\n{k}}}\n")
                pre+=(f"{k}inlet {pl['ocid']}From{ctx} is {pl['oty']} with {{\n"
                      f'{k}  briefly "What From{ctx} makes of that service\'s news"\n{k}}}\n')
                # the Intake connector is INTRA-context, so it lives here
                pre+=(f"{k}connector 'From{ctx} Intake' is from outlet "
                      f"{pl['ocid']}.From{ctx}.From{ctx}To{pl['ocid']} to inlet "
                      f"{pl['ocid']}.{pl['ocid']}From{ctx} with {{\n"
                      f'{k}  briefly "What From{ctx} makes of that news, on its way in"\n{k}}}\n')
            rep=f"{hm.group(1)}{hm.group(2)} as {shape_for(nout,nin)} is {{\n"+pre
            edits.append((oc["file"], s0, s0+hm.end(), rep))
        apply_edits(d, edits)

        # ---------- PASS 6: the connectors ----------
        ef=e.name; et=(d/ef).read_text()
        em=re.search(r"^(\s*)domain [\w.]+ is \{\n", et, re.M)
        if not em: raise RuntimeError("domain header")
        di=em.group(1)+"  "
        add=""
        for ctx,pl in plan.items():
            add+=(f"{di}persistent connector '{ctx}Event Stream' is from outlet "
                  f"{ctx}.{ctx}EventsOut to inlet {pl['ocid']}.From{ctx}.From{ctx}In with {{\n"
                  f'{di}  briefly "What {ctx} tells {pl["ocid"]}, unasked"\n{di}}}\n')
        (d/ef).write_text(et[:em.end()]+add+et[em.end():])
    except Exception as ex:
        err=str(ex)
    if not err:
        p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e.name],
                         cwd=d,capture_output=True,text=True)
        # errors only: since [1.25] the corpus legitimately carries Missing and style findings while it drains
        bad=[l for l in (p.stdout+p.stderr).splitlines() if re.match(r"^\[error\]",l.strip())]
        if bad: err="\n  ".join(bad[:6])
    if err:
        if not os.environ.get("KEEP"):
            for f,tx in snap.items(): (d/f).write_text(tx)
        print(f"REVERT {model}: {err}"); fail+=1
    else:
        print(f"OK     {model} ({len(rs)})"); ok+=1
print(f"\n{ok} models, {fail} reverted")
