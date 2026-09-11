#!/usr/bin/env python3
"""BACKLOG #38 item 4b: an asking adaptor forwards its answer as a local command.

Reid's ruling (2026-09-11): the adaptor is a translator. An answer obtained with
an ask/reply pair was obtained for a reason; the clause must turn it into a
message back to the originating context. Decisions per ask are in a TSV:

    idx<TAB>Entity.Command<TAB>field=expr,field=expr<TAB>[guard=<condition>]

`expr` is `askAnswer.<f>`, `<triggerBinding>.<f>` or `prompt("...")`; unlisted
fields take the trigger's same-named field if it has one, else a prompt. A
guard wraps the send in `when prompt("<condition>") then ... end`.

Per adaptor: an outlet back to its context (typed with the command, or an
alternation when it sends more than one), the context's inlet, the
`'<Adaptor> Intake'` connector, a boundary relay clause where the context
lacks one, ascriptions by arity. Rows whose target starts with `+` (a command
that does not exist yet) are left to add-commands.py.

One dump per model; edits by span descending; validate-and-revert per model.
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
    if ins==0: return "source"
    if outs==0: return "sink"
    if outs==1 and ins==1: return "flow"
    if outs>=2 and ins==1: return "split"
    if outs==1 and ins>=2: return "merge"
    return "router"
def words(s): return re.sub(r"(?<!^)(?=[A-Z])"," ",s).lower()
facts=json.load(open("/tmp/ask-facts.json"))
dec={}
for l in open(sys.argv[1]):
    p=l.rstrip("\n").split("\t")
    if len(p)<3 or not p[0].strip().isdigit(): continue
    dec[int(p[0])]=dict(target=p[1],mapping=p[2],guard=(p[3][6:] if len(p)>3 and p[3].startswith("guard=") else None))
only=set(sys.argv[2:])
bym=collections.defaultdict(list)
for i,f in enumerate(facts):
    if i in dec and not dec[i]["target"].startswith("+") and (not only or f["model"] in only): bym[f["model"]].append((i,f,dec[i]))
ok=fail=done=0
for model,items in sorted(bym.items()):
    d=ROOT/model; c=next(d.glob("*.conf")); e=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()).group(1)
    snap={str(f.relative_to(d)):f.read_text() for f in d.glob("**/*.riddl")}
    ns=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout))); byp={n["path"]:n for n in ns if "path" in n}
    edits=collections.defaultdict(list); hdr=collections.defaultdict(lambda:[0,0]); touched=0
    peradaptor=collections.defaultdict(list)   # adaptor path -> [(entity, cmd)]
    err=None
    try:
        for i,f,dcs in items:
            A=next((a for a in ns if a.get("kind")=="adaptor" and a["id"]==f["adaptor"] and byp[a["parent"]]["id"]==f["ctx"]),None)
            if not A: raise RuntimeError(f"[{i}] adaptor {f['adaptor']} not found")
            ctx=byp[A["parent"]]; ent,cmd=dcs["target"].split(".")
            cfields=f["commands"].get(cmd) if ent==f["entity"] else None
            if cfields is None:
                # a command of another entity in the same context (the answer belongs to it)
                cn=[n for n in ns if n.get("kind")=="command" and n["id"]==cmd and byp.get(n["parent"],{}).get("id")==ent and byp[n["parent"]].get("parent")==A["parent"]]
                if not cn: raise RuntimeError(f"[{i}] {ent}.{cmd} is not a command in {ctx['id']}")
                cfields=[(x["id"],None) for x in ns if x.get("kind")=="field" and x.get("parent")==cn[0]["path"]]
            # the ask clause
            cl=next((c for c in ns if c.get("kind")=="on-event" and c.get("path","").startswith(A["path"]+".") and (c.get("message") or {}).get("resolved","").endswith("."+f["trigger"])),None)
            if not cl: raise RuntimeError(f"[{i}] clause for {f['trigger']} not found in {A['id']}")
            b=cl.get("binding") if isinstance(cl.get("binding"),str) else (cl.get("binding") or {}).get("id")
            atxt=snap[A["file"]]; body=atxt[cl["span"]["start"]["offset"]:cl["span"]["end"]["offset"]]
            am=re.search(rf"let (\w+): type [\w.]+ = ask query [\w.]*{f['query']}\b[^\n]*\n(\s*do \"[^\"]*\"\n)?", body)
            if not am: raise RuntimeError(f"[{i}] ask {f['query']} not found in clause")
            answer=am.group(1)
            at=cl["span"]["start"]["offset"]+am.end()
            ind=re.match(r"[ \t]*", body[body.rfind("\n",0,am.start())+1:]).group(0)
            # field values
            mapping={}
            for part in re.split(r",(?=\w+=)", dcs["mapping"]) if dcs["mapping"] else []:
                k,v=part.split("=",1); mapping[k]=v
            tf={n for n,_ in f["trigger_fields"]}
            args=[]
            for fname,_ in cfields:
                if fname in mapping: v=mapping[fname].replace("askAnswer.",answer+".")
                elif fname in tf: v=f"{b}.{fname}"
                else: v=f'prompt("the {words(fname)} of this {words(cmd)}")'
                args.append(f"{fname} = {v}")
            outlet=f"{A['id']}To{ctx['id']}"
            stmt=f"send command {ent}.{cmd}({', '.join(args)}) to outlet {ctx['id']}.{A['id']}.{outlet}"
            if dcs["guard"]: stmt=f'when prompt("{dcs["guard"].replace("askAnswer.",answer+".")}") then\n{ind}  {stmt}\n{ind}end'
            edits[A["file"]].append((at,at,f"{ind}{stmt}\n"))
            peradaptor[A["path"]].append((ent,cmd)); touched+=1
        # per adaptor: the outlet back; per context: inlet, connector, relay
        ctxwork=collections.defaultdict(list)
        for ap,ecs in peradaptor.items():
            A=byp[ap]; ctx=byp[A["parent"]]; cmds=sorted({f"{e_}.{c_}" for e_,c_ in ecs})
            atxt=snap[A["file"]]; s0=A["span"]["start"]["offset"]
            hm=re.match(r"adaptor \w+ (?:from|to) context [\w.]+( as \w+)? is \{[ \t]*\n", atxt[s0:s0+300]); assert hm
            him=re.search(r"^(\s*)(inlet|outlet|handler) ", atxt[s0+hm.end():s0+hm.end()+600], re.M); ind=him.group(1) if him else "    "
            if [p for p in ns if p.get("kind")=="outlet" and p.get("parent")==ap and p["id"]==f"{A['id']}To{ctx['id']}"]:
                raise RuntimeError(f"{A['id']}: already has an outlet back to {ctx['id']}")
            oty=f"command {cmds[0]}" if len(cmds)==1 else f"type {A['id']}Command"
            edits[A["file"]].append((s0+hm.end(),s0+hm.end(),f"{ind}outlet {A['id']}To{ctx['id']} is {oty}\n")); hdr[ap][1]+=1
            ctxwork[ctx["path"]].append((A,cmds,oty))
        for cp,items_ in ctxwork.items():
            ctx=byp[cp]; ctxt=snap[ctx["file"]]; s0=ctx["span"]["start"]["offset"]
            hm=re.match(r"((?:\w+ )*context \w+)( as \w+)?( is \{[ \t]*\n)", ctxt[s0:s0+200]); assert hm, ctxt[s0:s0+80]
            H=[h for h in ns if h.get("kind")=="handler" and h.get("parent")==cp]
            if not H: raise RuntimeError(f"{ctx['id']}: no boundary handler")
            H=H[0]; relayed={(c.get("message") or {}).get("resolved","") for c in ns if c.get("kind")=="onmessageclause" and c.get("path","").startswith(H["path"]+".")}
            # the command stream outlet the relays use
            hb=ctxt[H["span"]["start"]["offset"]:H["span"]["end"]["offset"]]
            pre=""
            for A,cmds,oty in items_:
                if len(cmds)>1:
                    pre+=f"  type {A['id']}Command is one of {{\n    {' or '.join(cmds)}\n  }} with {{\n    briefly \"What {A['id']} turns its answers into\"\n  }}\n"
                pre+=f"  inlet {ctx['id']}From{A['id']} is {oty} with {{\n    briefly \"What {A['id']} makes of the answers it gets\"\n  }}\n"
                pre+=f"  connector '{A['id']} Intake' is from outlet {ctx['id']}.{A['id']}.{A['id']}To{ctx['id']} to inlet {ctx['id']}.{ctx['id']}From{A['id']} with {{\n    briefly \"Answers translated by {A['id']}, on their way in\"\n  }}\n"
                hdr[cp][0]+=1
                for ec in cmds:
                    ent,cmd=ec.split(".")
                    if not any(r.endswith(f".{ent}.{cmd}") for r in relayed):
                        sm=re.search(rf"send \w+ to outlet {ctx['id']}\.({ent}CommandStream\w*|\w*CommandStreamOut|\w*CommandsFwd)\n", hb)
                        if not sm: raise RuntimeError(f"{ctx['id']}: no relay outlet found for {ent}")
                        bname=cmd[0].lower()+cmd[1:]
                        hm2=re.match(r"\s*handler \w+ is \{[ \t]*\n", ctxt[H["span"]["start"]["offset"]:H["span"]["start"]["offset"]+120]); assert hm2
                        edits[ctx["file"]].append((H["span"]["start"]["offset"]+hm2.end(),H["span"]["start"]["offset"]+hm2.end(),f"    on {bname}: command {ent}.{cmd} is {{\n      send {bname} to outlet {ctx['id']}.{sm.group(1)}\n    }}\n"))
                        relayed.add(f".{ent}.{cmd}")
            edits[ctx["file"]].append((s0+hm.end(),s0+hm.end(),pre))
        for pth,(din,dout) in hdr.items():
            n=byp[pth]; t=snap[n["file"]]; s0=n["span"]["start"]["offset"]
            ins=len([p for p in ns if p.get("kind")=="inlet" and p.get("parent")==pth and "error-sink" not in json.dumps(p.get("options",""))])+din
            outs=len([p for p in ns if p.get("kind")=="outlet" and p.get("parent")==pth])+dout
            m=re.match(r"((?:\w+ )*?(?:adaptor \w+ (?:from|to) context [\w.]+|context \w+))( as \w+)?( is \{)", t[s0:s0+300]); assert m, t[s0:s0+80]
            edits[n["file"]].append((s0+m.start(1),s0+m.end(3),f"{m.group(1)} as {shape(outs,ins)}{m.group(3)}"))
    except Exception as ex: err=str(ex)
    if not err:
        for fpath,es in edits.items():
            t=snap[fpath]
            for s,t1,rep in sorted(es,key=lambda x:-x[0]): t=t[:s]+rep+t[t1:]
            (d/fpath).write_text(t)
        p=subprocess.run([R,"--provide-tips","--no-ansi-messages","validate",e],cwd=d,capture_output=True,text=True)
        bad=[l for l in (p.stdout+p.stderr).splitlines() if l.strip().startswith("[error]")]
        if bad: err="\n   ".join(bad[:3])
    if err:
        if not os.environ.get("KEEP"):
            for fpath,tx in snap.items(): (d/fpath).write_text(tx)
        print(f"REVERT {model}: {err[:300]}"); fail+=1
    else: print(f"OK     {model} ({touched})"); ok+=1; done+=touched
print(f"\n{ok} models ok, {fail} reverted, {done} asks forwarded")
