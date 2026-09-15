#!/usr/bin/env python3
"""HISTORICAL (2026-07-26): wired every model for A6 tell-reachability under the
unified streaming model. Kept because NOTEBOOK.md cites it; it predates A103
and [1.25], so the topology it describes is not the corpus's current one and
it must not be re-run.

Wire every model for A6 tell-reachability under the unified streaming model.

Topology per internal context (template validated on api-management):

    application context <Model>App          (one per model, in the domain file)
        outlet <E>Commands  ──► entity <E>.<E>Commands        [persistent]
        inlet  <R>Responses ◄── repository <R>.<R>Responses   [persistent]

    entity     E   inlet <E>Commands, outlet <E>Events
    split      <E>EventSplit  (only when E has >1 consumer)
    projector  P   inlet <P>In, outlet <P>Out
    repository R   inlet <R>From<X> per source, outlet <R>Responses

Shape ascriptions are deliberately omitted: absent is legal and only draws a
suppressible style nudge, whereas a wrong ascription is a hard error.
Port names are prefixed with their processor's name so they are unique within
the context (bare names like `Events` collide and resolve ambiguously).
"""
import re, glob, os, collections, sys

def strip(l):
    cut = len(l)
    for mk in ('|', '//'):
        i = l.find(mk)
        if i != -1: cut = min(cut, i)
    return re.sub(r'"[^"]*"', '""', l[:cut])

def bend(sl, s):
    """block end, char-level: stops at `} with {`"""
    d = 0; st = False
    for k in range(s, len(sl)):
        for ch in sl[k]:
            if ch == '{': d += 1; st = True
            elif ch == '}':
                d -= 1
                if st and d == 0: return k
    return len(sl) - 1

def defn_end(sl, s):
    """whole definition incl. its `with { }`"""
    d = 0
    for k in range(s, len(sl)):
        d += strip(sl[k]).count('{') - strip(sl[k]).count('}')
        if d == 0 and k > s: return k
    return len(sl) - 1

def ctx_of_files(files):
    """included file -> owning context (read includes from RAW lines)"""
    owner = {}
    for f in files:
        d = os.path.dirname(f); ctx = None
        for l in open(f).read().split("\n"):
            cm = re.match(r'\s*(?:application |external |gateway |service )?context\s+(\w+)\s+is\s*\{', strip(l))
            if cm: ctx = cm.group(1)
            im = re.match(r'\s*include\s+"([^"]+)"', l)
            if im and ctx: owner[os.path.normpath(os.path.join(d, im.group(1)))] = ctx
    return owner

def meta(brief, *desc):
    out = ["  } with {", f'    briefly "{brief}"', "    described as {"]
    out += [f"      |{d}" for d in desc]
    out += ["    }", "  }"]
    return out

def domain_of_files(files):
    """file -> the domain file that (transitively) includes it"""
    inc = {}
    for f in files:
        d = os.path.dirname(f)
        for l in open(f).read().split("\n"):
            im = re.match(r'\s*include\s+"([^"]+)"', l)
            if im: inc.setdefault(f, []).append(os.path.normpath(os.path.join(d, im.group(1))))
    domfiles = [f for f in files
                if any(re.match(r'\s*domain\s+\w+\s+is\s*\{', strip(l)) for l in open(f).read().split("\n"))]
    domset = set(domfiles)
    owner = {}
    for df in domfiles:
        stack = list(inc.get(df, []))
        while stack:
            x = stack.pop()
            if x in domset: continue          # a nested domain owns its own subtree
            if x in owner: continue
            owner[x] = df
            stack += inc.get(x, [])
    for df in domfiles: owner[df] = df
    return owner

def wire_model(R):
    files = sorted(glob.glob(os.path.join(R, "**", "*.riddl"), recursive=True))
    owner = ctx_of_files(files)
    domof = domain_of_files(files)
    alltxt = "\n".join(open(f).read() for f in files)

    # ---- discover per-context processors, and where each is declared -------
    ctxs = collections.defaultdict(lambda: {"ent": {}, "repo": {}, "proj": {}, "ext": False, "file": None})
    for f in files:
        raw = open(f).read().split("\n"); sl = [strip(l) for l in raw]
        selfctx = None
        for i, s in enumerate(sl):
            cm = re.match(r'\s*(application |external |gateway |service )?context\s+(\w+)\s+is\s*\{', s)
            if cm:
                selfctx = cm.group(2)
                ctxs[selfctx]["ext"] = (cm.group(1) or '').strip() == 'external'
                ctxs[selfctx]["file"] = f
        c = selfctx or owner.get(os.path.normpath(f))
        if not c: continue
        for i, s in enumerate(sl):
            for kind, key in (("entity", "ent"), ("repository", "repo"), ("projector", "proj")):
                m = re.match(r'\s*'+kind+r'\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{', s)
                if m: ctxs[c][key][m.group(1)] = f

    internal = {c: v for c, v in ctxs.items()
                if not v["ext"] and v["ent"] and v["repo"] and v["file"]}
    if not internal: return 0

    taken = set(re.findall(r'^\s*(?:inlet|outlet)\s+(\w+)\s', alltxt, re.M))
    def uniq(name):
        n = name; i = 2
        while n in taken: n = f"{name}{i}"; i += 1
        taken.add(n); return n

    edits = collections.defaultdict(list)   # file -> [(line_idx, lines, replace_upto)]
    app_out = collections.defaultdict(list); app_in = collections.defaultdict(list)
    portname = {}
    evs_of = {}
    model = os.path.basename(R)
    dom_default = os.path.join(R, os.path.basename(R) + '.riddl')
    app = "".join(w.capitalize() for w in re.split(r'[-_]', model)) + "App"

    ctxfiles = collections.defaultdict(set)
    for f in files:
        oc = owner.get(os.path.normpath(f))
        if oc: ctxfiles[oc].add(f)
    for c2, v2 in ctxs.items():
        if v2["file"]: ctxfiles[c2].add(v2["file"])

    for c, v in internal.items():
        ents, repos, projs = list(v["ent"]), list(v["repo"]), list(v["proj"])
        repo = repos[0]; repo_file = v["repo"][repo]
        evtype = {}
        for e in ents:
            evtype[e] = f"{e}Event" if re.search(r'\btype\s+'+e+r'Event\s+is\s+one\s+of', alltxt) else None

        # ---- entity: command inlet + event outlet -------------------------
        for e in ents:
            f = v["ent"][e]; raw = open(f).read().split("\n"); sl = [strip(l) for l in raw]
            i = next((k for k, s in enumerate(sl) if re.match(r'\s*entity\s+'+e+r'\s+(?:as\s+\w+\s+)?is\s*\{', s)), None)
            if i is None: continue
            ee = bend(sl, i)
            if re.search(r'^\s*(inlet|outlet)\s', "\n".join(sl[i:ee+1]), re.M): continue
            cmds = [m.group(1) for k in range(i, ee+1) if (m := re.match(r'\s*command\s+(\w+)\s+is', sl[k]))]
            evs  = [m.group(1) for k in range(i, ee+1) if (m := re.match(r'\s*event\s+(\w+)\s+is', sl[k]))]
            if not evs: continue
            evs_of[e] = evs
            ind = re.match(r'\s*', raw[i]).group(0)
            ct = f"{e}Command"
            blk = []
            if re.search(r'\b(type|record|command|event|query|result)\s+'+ct+r'\b', alltxt):
                ct = f"{e}CommandSet"
            if cmds and not re.search(r'\btype\s+'+ct+r'\s+is\s+one\s+of', alltxt):
                blk += [ind+f"  type {ct} is one of {{"]
                blk += [ind+f"    {e}.{x}," for x in cmds[:-1]] + [ind+f"    {e}.{cmds[-1]}"]
                blk += [ind+"  } with {", ind+f'    briefly "{e} command alternation"',
                        ind+"    described as {", ind+f"      |Commands accepted by the {e} entity.",
                        ind+"    }", ind+"  }"]
            et = evtype[e]
            if not et:
                cand = next((n for n in (f"{e}Event", f"{e}StreamEvent")
                             if re.search(r'\btype\s+'+n+r'\s+is\s+one\s+of', alltxt)), None)
                if cand:
                    et = cand; evtype[e] = cand
                else:
                    et = f"{e}Event"
                    if re.search(r'\b(type|record|command|event|query|result)\s+'+et+r'\b', alltxt):
                        et = f"{e}StreamEvent"
                    blk += [ind+f"  type {et} is one of {{"]
                    blk += [ind+f"    {e}.{x}," for x in evs[:-1]] + [ind+f"    {e}.{evs[-1]}"]
                    blk += [ind+"  } with {", ind+f'    briefly "{e} event alternation"',
                            ind+"    described as {", ind+f"      |Events published by the {e} entity.",
                            ind+"    }", ind+"  }"]
                    evtype[e] = et
            ports = []
            cin = uniq(f"{e}Commands"); cout = uniq(f"{e}Events")
            portname[(c, e, "in")] = cin; portname[(c, e, "out")] = cout
            if cmds: ports.append(ind+f"  inlet {cin} is type {ct}")
            ports.append(ind+f"  outlet {cout} is type {et}")
            edits[f].append((i+1, blk+ports, None))
            if cmds:
                app_out[domof.get(os.path.normpath(v['file']), dom_default)].append((c, e, ct))

        # ---- projector: in/out -------------------------------------------
        for p in projs:
            f = v["proj"][p]; raw = open(f).read().split("\n"); sl = [strip(l) for l in raw]
            i = next((k for k, s in enumerate(sl) if re.match(r'\s*projector\s+'+p+r'\s+(?:as\s+\w+\s+)?is\s*\{', s)), None)
            if i is None: continue
            if re.search(r'^\s*(inlet|outlet)\s', "\n".join(sl[i:bend(sl,i)+1]), re.M): continue
            et = evtype.get(ents[0]) if ents else None
            if not et: continue
            ind = re.match(r'\s*', raw[i]).group(0)
            pports = []
            for e2 in ents:
                if not evtype.get(e2) or e2 not in evs_of: continue
                nm = uniq(f"{p}From{e2}")
                portname[(c, p, "in", e2)] = nm
                pports.append(ind+f"  inlet {nm} is type {evtype[e2]}")
            if not pports: continue
            pout = uniq(f"{p}Out")
            portname[(c, p, "out")] = pout
            pports.append(ind+f"  outlet {pout} is type {et}")
            edits[f].append((i+1, pports, None))

        # ---- every repository: one inlet per source + a response outlet ----
        for rp in repos:
            rfile = v["repo"][rp]
            raw = open(rfile).read().split("\n"); sl = [strip(l) for l in raw]
            i = next((k for k, sx in enumerate(sl)
                      if re.match(r'\s*repository\s+'+rp+r'\s+(?:as\s+\w+\s+)?is\s*\{', sx)), None)
            if i is None: continue
            if re.search(r'^\s*(inlet|outlet)\s', "\n".join(sl[i:bend(sl,i)+1]), re.M): continue
            ind = re.match(r'\s*', raw[i]).group(0)
            et = evtype.get(ents[0]) if ents else None
            res = None
            for ff in sorted(ctxfiles.get(c, [])):
                tl = [strip(x) for x in open(ff).read().split("\n")]
                encl_here = []
                for k2, sx2 in enumerate(tl):
                    em2 = re.match(r'\s*(?:entity|repository|projector|adaptor|processor)\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{', sx2)
                    if em2: encl_here.append((em2.group(1), k2, bend(tl, k2)))
                for k, sx in enumerate(tl):
                    rm2 = re.match(r'\s*result\s+(\w+)\s+is', sx)
                    if not rm2: continue
                    encl = next((n for n, a, b in encl_here if a < k < b), None)
                    res = f"{encl}.{rm2.group(1)}" if encl else rm2.group(1)
                    break
                if res: break
            ports = []
            for e in ents:
                if not evtype.get(e) or e not in evs_of: continue
                nm = uniq(f"{rp}From{e}"); portname[(c, rp, e)] = nm
                ports.append(ind+f"  inlet {nm} is type {evtype[e]}")
            if rp == repos[0]:
                for pj in projs:
                    if et and (c, pj, "out") in portname:
                        nm = uniq(f"{rp}From{pj}"); portname[(c, rp, pj)] = nm
                        ports.append(ind+f"  inlet {nm} is type {et}")
            if res:
                nm = uniq(f"{rp}Responses"); portname[(c, rp, "out")] = nm
                ports.append(ind+f"  outlet {nm} is type {res}")
                app_in[domof.get(os.path.normpath(v['file']), dom_default)].append((c, rp, res))
            if ports: edits[rfile].append((i+1, ports, None))

        # ---- split processors + intra-context connectors ------------------
        conns = []
        cf = v["file"]; craw = open(cf).read().split("\n")
        cidx = max(k for k, l in enumerate(craw) if re.match(r'^\}\s*with\s*\{', l))
        blocks = []
        for e in ents:
            et = evtype.get(e)
            if not et or e not in evs_of: continue
            consumers = [("repo", r) for r in repos] + [("proj", p) for p in projs]
            if len(consumers) == 1:
                kind, tgt = consumers[0]
                key = (c, tgt, e) if kind == "repo" else (c, tgt, "in", e)
                if key not in portname: continue
                dst = f"{c}.{tgt}.{portname[key]}"
                conns.append((f"Link{e}To{tgt}", f"{c}.{e}.{portname[(c,e,'out')]}", dst, False))
            else:
                sp = f"{e}EventSplit"
                blocks += [f"  processor {sp} is {{", f"    inlet {sp}In is type {et}"]
                for kind, tgt in consumers:
                    blocks.append(f"    outlet {sp}To{tgt} is type {et}")
                blocks.append(f"    handler {sp}Handler is {{")
                for ev in evs_of[e]:
                    blocks.append(f"      on event {e}.{ev} is {{")
                    for kind2, tgt2 in consumers:
                        blocks.append(f"        send event {e}.{ev} to outlet {sp}To{tgt2}")
                    blocks.append(f"        tell event {e}.{ev} to entity {c}.{e}")
                    blocks.append(f"      }}")
                blocks.append(f"      on other is {{")
                blocks.append(f'        error "Unexpected message for processor {sp}"')
                blocks.append(f"      }}")
                blocks.append(f"    }} with {{")
                blocks.append(f'      briefly "{e} event fan-out handler"')
                blocks.append(f"      described as {{")
                blocks.append(f"        |Delivers each {e} event to all of its consumers.")
                blocks.append(f"      }}")
                blocks.append(f"    }}")
                blocks += meta(f"{e} event fan-out", f"Fans {e} events out to the repository and projectors.")
                conns.append((f"Link{e}To{sp}", f"{c}.{e}.{portname[(c,e,'out')]}", f"{c}.{sp}.{sp}In", False))
                for kind, tgt in consumers:
                    key = (c, tgt, e) if kind == "repo" else (c, tgt, "in", e)
                    if key not in portname: continue
                    dst = f"{c}.{tgt}.{portname[key]}"
                    conns.append((f"Link{sp}To{tgt}", f"{c}.{sp}.{sp}To{tgt}", dst, False))
        for p in projs:
            if (c, p, 'out') not in portname or (c, repo, p) not in portname: continue
            conns.append((f"Link{p}To{repo}", f"{c}.{p}.{portname[(c,p,'out')]}", f"{c}.{repo}.{portname[(c,repo,p)]}", False))
        for n, src, dst, _ in conns:
            blocks += [f"  connector {n} is {{", f"    from outlet {src} to",
                       f"      inlet {dst}", "  } with {", f'    briefly "{n}"', "  }"]
        if blocks: edits[cf].append((cidx, blocks, None))

    # ---- one application context per DOMAIN file ------------------------
    for dom in sorted(set(list(app_out) + list(app_in))):
        if not os.path.exists(dom): continue
        outs, ins_ = app_out.get(dom, []), app_in.get(dom, [])
        if not outs and not ins_: continue
        dn = None
        for l in open(dom).read().split("\n"):
            dm = re.match(r'\s*domain\s+(\w+)\s+is\s*\{', strip(l))
            if dm: dn = dm.group(1); break
        if not dn: dn = re.sub(r'[^A-Za-z0-9]', '', os.path.basename(dom)[:-6]).capitalize()
        app = dn + "App"
        draw = open(dom).read().split("\n")
        didx = max(k for k, l in enumerate(draw) if re.match(r'^\}\s*with\s*\{', l))
        blk = [f"  application context {app} is {{"]
        for c, e, ct in outs: blk.append(f"    outlet App{e}Commands is type {c}.{e}.{ct}")
        for c, r, res in ins_: blk.append(f"    inlet App{r}Responses is type {c}.{res}")
        blk += [f"    handler {app}Handler is {{", "      on other is {",
                f'        error "Unexpected message for application context {app}"',
                "      }", "    } with {", f'      briefly "{app} handler"',
                "      described as {", "        |Originates commands and receives query responses.",
                "      }", "    }"]
        blk += meta(f"{app} application",
                    "Placeholder for the UI-bearing application that originates",
                    "commands and consumes query responses.")
        xc = []
        for c, e, ct in outs:
            xc.append((f"LinkApp{e}Commands", f"{app}.App{e}Commands", f"{c}.{e}.{portname[(c,e,'in')]}"))
        for c, r, res in ins_:
            xc.append((f"LinkApp{r}Responses", f"{c}.{r}.{portname[(c,r,'out')]}", f"{app}.App{r}Responses"))
        for n, src, dst in xc:
            blk += [f"  connector {n} is {{", f"    from outlet {src} to", f"      inlet {dst}",
                    "  } with {", "    option is persistent", f'    briefly "{n}"', "  }"]
        draw[didx:didx] = blk
        open(dom, "w").write("\n".join(draw))

    for f, ins in edits.items():
        raw = open(f).read().split("\n")
        for idx, block, repl in sorted(ins, key=lambda x: -x[0]):
            if repl is None: raw[idx:idx] = block
            else: raw[idx:idx+1] = block
        open(f, "w").write("\n".join(raw))
    return 1

if __name__ == "__main__":
    targets = sys.argv[1:] or sorted({os.path.dirname(c) for c in glob.glob("**/*.conf", recursive=True)})
    n = sum(wire_model(R) for R in targets)
    print(f"models wired: {n}")
