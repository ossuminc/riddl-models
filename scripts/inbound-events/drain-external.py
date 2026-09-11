#!/usr/bin/env python3
"""BACKLOG #38 item 2a: the channel for a From-adaptor that handles an external
context's events when that context has no outlet.

These are the hand-written `XAdapter`s the inbound campaign never touched: real
clauses, no channel. Per (adaptor, external context X):
  - X gains `outlet <X>EventsOut` typed with the alternation of X's declared
    events the adaptor handles (declared as `type <X>Event` when >1),
  - every `yield <v>` / `yield event E(...)` in X's handlers for one of those
    events gains a `send` of the same to that outlet (a yield answers the
    SENDER; the send is the broadcast),
  - the adaptor gains `inlet <Adaptor>In` of that type and an ascription by arity,
  - the domain gains `persistent connector '<X>Event Stream'`.
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
    if outs==0 and ins==0: return "void"
    if ins==0: return "source"
    if outs==0: return "sink"
    if outs==1 and ins==1: return "flow"
    if outs>=2 and ins==1: return "split"
    if outs==1 and ins>=2: return "merge"
    return "router"
want=collections.defaultdict(set)
for l in open(sys.argv[1] if len(sys.argv)>1 and sys.argv[1].endswith(".jsonl") else "/tmp/sweep47b.jsonl"):
    r=json.loads(l)
    if r["rule"]=="stream-processor-no-inlet" and r["message"].startswith("Adaptor"):
        want[r["model"]].add(re.match(r"Adaptor '(\w+)'",r["message"]).group(1))
ok=fail=done=0
for model in sorted(want):
    d=ROOT/model; c=next(d.glob("*.conf")); e=re.search(r'input-file\s*=\s*"?([^"\s]+)"?',c.read_text()).group(1)
    snap={str(f.relative_to(d)):f.read_text() for f in d.glob("**/*.riddl")}
    ns=list(nodes(json.loads(subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True).stdout)))
    byp={n["path"]:n for n in ns if "path" in n}
    edits=collections.defaultdict(list); hdr=collections.defaultdict(lambda:[0,0]); touched=0; seen=set()
    xdone=set()
    for aname in sorted(want[model]):
        for a in [x for x in ns if x.get("kind")=="adaptor" and x["id"]==aname and not (x["path"] in seen or seen.add(x["path"]))]:
            evp={(c.get("message") or {}).get("resolved") for c in ns if c.get("kind")=="on-event" and c.get("path","").startswith(a["path"]+".")}
            owners={x.rsplit(".",1)[0] for x in evp if x}
            if len(owners)!=1: continue
            X=byp.get(list(owners)[0])
            if not X or X.get("kind")!="context" or X.get("intention")!="External": continue
            if [p for p in ns if p.get("kind")=="outlet" and p.get("parent")==X["path"]] or X["path"] in xdone:
                print(f"SKIP {model.split('/')[-1]}/{aname}: {X['id']} already has an outlet"); continue
            xdone.add(X["path"])
            evs=sorted(x.split(".")[-1] for x in evp)
            xt=snap[X["file"]]; xs,xe=X["span"]["start"]["offset"],X["span"]["end"]["offset"]; xb=xt[xs:xe]
            hm=re.match(r"external context \w+( as \w+)? is \{[ \t]*\n", xb); assert hm, xb[:60]
            bi=re.search(r"^(\s*)(type|inlet|outlet|handler|command|event|query|result) ", xb[hm.end():hm.end()+4000], re.M); xi=bi.group(1) if bi else "  "
            if len(evs)>1:
                pre=f"{xi}type {X['id']}Event is one of {{\n{xi}  {' or '.join(evs)}\n{xi}}} with {{\n{xi}  briefly \"Everything this service tells the model, unasked\"\n{xi}}}\n"; xty=f"type {X['id']}Event"; aty=f"type {X['id']}.{X['id']}Event"
            else: pre=""; xty=f"event {evs[0]}"; aty=f"event {X['id']}.{evs[0]}"
            pre+=f"{xi}outlet {X['id']}EventsOut is {xty} with {{\n{xi}  briefly \"What this service tells the model, unasked\"\n{xi}}}\n"
            edits[X["file"]].append((xs+hm.end(),xs+hm.end(),pre)); hdr[X["path"]][1]+=1
            # sends beside yields, for the events the outlet carries
            n=0
            for m in re.finditer(r"^(\s*)yield (\w+)\n", xb, re.M):
                # value form: find the let that typed it
                lm=re.search(rf"let {m.group(2)}: type (\w+)", xb[:m.start()][-600:])
                if lm and lm.group(1) in evs:
                    at=xs+m.end(); edits[X["file"]].append((at,at,f"{m.group(1)}send {m.group(2)} to outlet {X['id']}.{X['id']}EventsOut\n")); n+=1
            for m in re.finditer(r"^(\s*)yield event (\w+)(\(.*\))\n", xb, re.M):
                if m.group(2) in evs:
                    at=xs+m.end(); edits[X["file"]].append((at,at,f"{m.group(1)}send event {m.group(2)}{m.group(3)} to outlet {X['id']}.{X['id']}EventsOut\n")); n+=1
            # the adaptor's inlet
            at_=snap[a["file"]]; s0=a["span"]["start"]["offset"]; ab=at_[s0:a["span"]["end"]["offset"]]
            am=re.match(r"adaptor \w+ (?:from|to) context [\w.]+( as \w+)? is \{[ \t]*\n", ab); assert am, ab[:80]
            him=re.search(r"^(\s*)(inlet|outlet|handler) ", ab[am.end():], re.M); ind=him.group(1) if him else "    "
            edits[a["file"]].append((s0+am.end(),s0+am.end(),f"{ind}inlet {aname}In is {aty}\n")); hdr[a["path"]][0]+=1
            # the domain connector
            et=snap[e]; em=re.search(r"^(\s*)domain [\w.]+ is \{\n", et, re.M); di=em.group(1)+"  "; ctxn=byp[a["parent"]]
            edits[e].append((em.end(),em.end(),f"{di}persistent connector '{X['id']}Event Stream' is from outlet {X['id']}.{X['id']}EventsOut to inlet {ctxn['id']}.{aname}.{aname}In with {{\n{di}  briefly \"What {X['id']} tells {ctxn['id']}, unasked\"\n{di}}}\n"))
            print(f"WIRE {model.split('/')[-1]}/{aname} <- {X['id']} [{', '.join(evs)}] sends+{n}"); touched+=1
    for pth,(din,dout) in hdr.items():
        nd=byp[pth]; t=snap[nd["file"]]; s0=nd["span"]["start"]["offset"]
        ins=len([p for p in ns if p.get("kind")=="inlet" and p.get("parent")==pth])+din
        outs=len([p for p in ns if p.get("kind")=="outlet" and p.get("parent")==pth])+dout
        m=re.match(r"((?:\w+ )*?(?:adaptor \w+ (?:from|to) context [\w.]+|external context \w+))( as \w+)?( is \{)", t[s0:s0+300]); assert m, t[s0:s0+80]
        asc=f" as {shape(outs,ins)}" if (ins and outs) else ""
        edits[nd["file"]].append((s0+m.start(1),s0+m.end(3),f"{m.group(1)}{asc}{m.group(3)}"))
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
print(f"\n{ok} models ok, {fail} reverted, {done} adaptors wired")
