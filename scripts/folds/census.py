#!/usr/bin/env python3
"""Census of prose folds: an `on event` clause in an event-sourced entity whose
every statement is `do "…"` or `set … to prompt(…)` (riddlc's Fold.Prose,
`entity-event-sourced-prose-folds`). For each, print what the fold could say:
the state record's fields beside the event's fields.

    ./scripts/folds/census.py [model-dir…]  > scripts/folds/census.tsv
"""
import json,re,subprocess,sys,os
from pathlib import Path
ROOT=Path("/Users/reid/Code/ossuminc/riddl-models"); R="/Users/reid/Code/ossuminc/bin/riddlc"
def nodes(n):
    if isinstance(n,dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n,list):
        for v in n: yield from nodes(v)
def clause_end(txt,start):
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
def models(args):
    if args: return [ROOT/a for a in args]
    out=[]
    for c in ROOT.rglob("*.conf"):
        if "patterns" in c.parts or "/1/" in str(c): continue
        out.append(c.parent)
    return sorted(set(out))
def entry(d):
    for c in d.glob("*.conf"):
        m=re.search(r'input-file\s*=\s*"([^"]+)"',c.read_text())
        if m: return m.group(1)
def main():
    for d in models(sys.argv[1:]):
        e=entry(d)
        if not e: continue
        p=subprocess.run([R,"dump",e,"--json"],cwd=d,capture_output=True,text=True)
        try: ns=list(nodes(json.loads(p.stdout)))
        except Exception: print(f"# {d}: dump failed",file=sys.stderr); continue
        byp={n["path"]:n for n in ns if "path" in n}
        texts={}
        def text(f):
            fp=(d/e).parent/f
            if fp not in texts: texts[fp]=fp.read_text()
            return texts[fp]
        fields={}
        for n in ns:
            if n["kind"]=="field": fields.setdefault(n["parent"],[]).append((n["id"],n.get("type",""),n.get("cardinality","")))
        for ent in [n for n in ns if n["kind"]=="entity" and "EventSourced" in n.get("intentions",[])]:
            states=[n for n in ns if n["kind"]=="state" and n["parent"]==ent["path"]]
            for cl in [n for n in ns if n["kind"]=="on-event" and ent["path"] in n.get("ancestors",[])]:
                txt=text(cl["file"]); s=cl["span"]["start"]["offset"]; body=txt[s:clause_end(txt,s)]
                flat=re.sub(r'"(?:[^"\\]|\\.)*"','""',body,flags=re.S)   # blank string literals, multi-line ones too
                stmts=[l.strip() for l in flat.split("\n")[1:-1] if l.strip() and not l.strip().startswith("//")]
                prose=all(l.startswith('do ') or re.match(r'set .* to prompt\(',l) for l in stmts)
                if not prose: continue
                ev=cl["message"]["resolved"]
                # every state of the entity, with its record's fields; the fold names one (or none)
                m=re.search(r"set state (\S+)",body); st=m.group(1).split(".")[-1] if m else "?"
                sts=[]
                for stn in states:
                    stxt=text(stn["file"]); mm=re.match(r"\s*(?:initial )?state \S+ of (?:record )?(\S+)",stxt[stn["span"]["start"]["offset"]:]); rec=mm.group(1).split(".")[-1] if mm else "?"
                    recpath=next((p for p in byp if p.split(".")[-1]==rec and byp[p]["kind"] in("record","type") and ent["path"] in byp[p].get("ancestors",[])+[byp[p]["parent"]]),None)
                    rf=fields.get(recpath,[])
                    sts.append(stn["id"]+"{"+", ".join(f"{a}:{b.replace('type ','')}{'?' if c=='zero-or-one' else ('*' if c=='zero-or-more' else ('+' if c=='one-or-more' else ''))}" for a,b,c in rf)+"}")
                rf=[]; ef=fields.get(ev,[])
                rec=" ; ".join(sts)
                print("\t".join([str(d.relative_to(ROOT)),ent["path"],ev.split(".")[-1],st,rec,cl["file"],str(cl["span"]["start"]["line"]),
                    ", ".join(f"{a}:{b}{'?' if c=='zero-or-one' else ''}" for a,b,c in rf), ", ".join(f"{a}:{b}" for a,b,c in ef), " | ".join(stmts)]))
main()
