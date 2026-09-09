#!/usr/bin/env python3
"""Setup-path applier: give a placeholder adaptor real plumbing and a driver.

Transactional per MODEL: every file it will touch is snapshotted first, the
whole model's pairs are applied, riddlc validates, and on ANY finding the
snapshot is restored.  Line positions come from `riddlc dump --json` spans,
never from a grammar regex.
"""
import os
import json, os, re, shutil, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
# a relative RIDDLC is resolved against the repo root, since these
# scripts change directory per model (same rule as collect-warnings.py)
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = _r if os.path.isabs(_r) else str((ROOT / _r).resolve())

def entry_of(d):
    for c in d.glob("*.conf"):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        return d / (m.group(1) if m else f"{d.name}.riddl")

def nodes(n):
    if isinstance(n, dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)

def dump(d, e):
    p = subprocess.run([RIDDLC, "dump", e.name, "--json"], cwd=d,
                       capture_output=True, text=True)
    return list(nodes(json.loads(p.stdout)))

def validate(d, e):
    p = subprocess.run([RIDDLC, "--provide-tips", "--no-ansi-messages",
                        "validate", e.name], cwd=d, capture_output=True, text=True)
    txt = p.stdout + p.stderr
    bad = [l for l in txt.splitlines()
           if re.match(r"^\[(error|warning|style|usage|missing|completeness)\]", l.strip())]
    return bad, txt

TO = re.compile(r'adaptor\s+(\w+)\s+to\s+context\s+([\w.]+)')

def apply_model(model, recs, dry=False):
    d = ROOT / model; e = entry_of(d)
    ns = dump(d, e)
    edits = defaultdict(list)          # file -> [(lineno0, ndelete, [newlines])]
    for r in recs:
        ctx = r["ctx"]
        # --- locate the outbound adaptor ---
        ad = None
        for a in ns:
            if a.get("kind") != "adaptor": continue
            src = (d / a["file"]).read_text().splitlines()
            m = TO.search(src[a["span"]["start"]["line"]-1][a["span"]["start"]["col"]-1:])
            if m and m.group(2).split(".")[-1] == ctx:
                ad, adname = a, m.group(1); break
        assert ad, f"{model}: no outbound adaptor to {ctx}"
        ctxname = ad["parent"].split(".")[-1]
        af = ad["file"]; asrc = (d / af).read_text().splitlines()
        decl_i = ad["span"]["start"]["line"] - 1

        wired = [c for cl in r["clauses"] for c, _ in cl["sends"]]
        keep  = r.get("keep", [])
        multi = len(wired) + len(keep) > 1
        outlet = f"{adname}Out"
        otype = (f"type {ctx}.{ctx}Command" if multi else f"command {ctx}.{wired[0]}")

        # 1. ascription + outlet on the adaptor
        line = asrc[decl_i]
        assert " as " not in line, f"{model}/{ctx}: adaptor already ascribed"
        edits[af].append((decl_i, 1, [line.replace(" is {", " as flow is {", 1),
                                      f"    outlet {outlet} is {otype}"]))

        # 2. clauses of this adaptor's handler
        hnd = next(h for h in ns if h.get("kind") == "handler" and h.get("parent") == ad["path"])
        cls = [c for c in ns if c.get("parent") == hnd["path"]
               and c.get("kind") in ("onmessageclause", "on-event", "on-other")]
        other = next(c for c in cls if c["kind"] == "on-other")
        # delete the placeholder clause for every command we are wiring
        for c in cls:
            if c["kind"] != "onmessageclause": continue
            txt = asrc[c["span"]["start"]["line"]-1]
            if any(re.search(rf"\b{ctx}\.{w}\b", txt) for w in wired):
                s = c["span"]["start"]["line"]-1; en = c["span"]["end"]["line"]-1
                edits[af].append((s, en - s, []))
        # insert the driving clauses just before `on other`
        new = []
        for cl in r["clauses"]:
            ev = cl["event"]; b = ev.split(".")[-1]; b = b[0].lower() + b[1:]
            new.append(f"      on {b}: event {ev} is {{")
            for i, (cmd, why) in enumerate(cl["sends"]):
                new.append(f'        let item{i}: type {ctx}.{cmd} = prompt("translate the {b} event into a {cmd}, {why}")')
                new.append(f"        send item{i} to outlet {ctxname}.{adname}.{outlet}")
            new.append("      }")
        edits[af].append((other["span"]["start"]["line"]-1, 0, new))

        # 3. the external context gains a sink boundary
        ext = next(c for c in ns if c.get("kind") == "context"
                   and c.get("id") == ctx and c.get("intention") == "External")
        ef = ext["file"]; esrc = (d / ef).read_text().splitlines()
        ei = ext["span"]["start"]["line"] - 1
        assert " as " not in esrc[ei], f"{model}/{ctx}: external context already ascribed"
        blk = [esrc[ei].replace(" is {", " as sink is {", 1)]
        allc = wired + keep
        q = f"{ctx}." if r.get("qualify") else ""
        if multi:
            blk += [f"  type {ctx}Command is one of {{",
                    "    " + " or ".join(q + c for c in allc),
                    "  } with {",
                    '    briefly "Everything this service can be asked to send"',
                    "  }",
                    f"  inlet {ctx}Requests is type {ctx}Command with {{",
                    '    briefly "What this context asks the service to send"',
                    "  }"]
        else:
            blk += [f"  inlet {ctx}Requests is command {q}{allc[0]} with {{",
                    '    briefly "What this context asks the service to send"',
                    "  }"]
        blk.append(f"  handler {ctx}Boundary is {{")
        for c in allc:
            blk += [f"    on command {q}{c} is {{", '      do "deliver it to the recipient"', "    }"]
        blk += ["    on other is {",
                f'      error "Unexpected message for external context {ctx}"',
                "    }", "  } with {", f'    briefly "{ctx} boundary"', "  }"]
        edits[ef].append((ei, 1, blk))

        # 4. the connector, beside the model root's other persistent ones
        rf = e.name; rsrc = (d / rf).read_text().splitlines()
        ri = next(i for i, l in enumerate(rsrc) if l.startswith("  persistent connector "))
        edits[rf].append((ri, 0, [
            f"  persistent connector '{ctx}Request Stream' is from outlet {ctxname}.{adname}.{outlet} to inlet {ctx}.{ctx}Requests with {{",
            f'    briefly "What {ctxname} asks {ctx} to send"', "  }"]))

    if dry:
        for f, es in edits.items():
            print(f"-- {f}")
            for i, n, new in sorted(es): print(f"   @{i+1} -{n} +{len(new)}")
        return True

    snap = {f: (d / f).read_text() for f in edits}
    try:
        for f, es in edits.items():
            lines = (d / f).read_text().splitlines()
            for i, n, new in sorted(es, key=lambda x: -x[0]):
                lines[i:i+n] = new
            (d / f).write_text("\n".join(lines) + "\n")
        bad, txt = validate(d, e)
        if bad:
            raise RuntimeError("\n".join(bad[:12]))
    except Exception as ex:
        for f, t in snap.items(): (d / f).write_text(t)
        print(f"REVERT {model}: {ex}")
        return False
    print(f"OK     {model}  ({len(recs)} pair(s))")
    return True

recs = defaultdict(list)
for l in open(sys.argv[1]):
    r = json.loads(l); recs[r["model"]].append(r)
dry = "--dry" in sys.argv
ok = fail = 0
for m, rs in recs.items():
    if apply_model(m, rs, dry): ok += 1
    else: fail += 1
print(f"\n{ok} models applied, {fail} reverted")
