#!/usr/bin/env python3
"""Census of unsent commands owned by EXTERNAL contexts.

Method (BACKLOG #33 "The census, and how to rebuild it"):
  1. external contexts are kind == "context" with intention == "External"
  2. a command is UNSENT unless something drives it
  3. an unsent command owned by an external context is a wiring gap

Step 2 is the trap: the wiring idiom is
    let notice: type Far.Cmd = prompt(...)
    send notice to outlet ...
and a `send` of a BOUND value carries NO message ref -- its message is
{"value": "notice"}.  So a driver is EITHER a tell/send/forward message ref
OR a let-statement's declaredType.resolved.
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
# a relative RIDDLC is resolved against the repo root, since this script
# changes directory per model (same rule as collect-warnings.py)
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()
INPUT_FILE = re.compile(r'^\s*input-file\s*=\s*"?([^"\s]+)"?', re.MULTILINE)

def models():
    out = []
    for c in sorted(ROOT.rglob("*.conf")):
        if "patterns" in c.relative_to(ROOT).parts: continue
        m = INPUT_FILE.search(c.read_text())
        out.append((c.parent, c.parent / (m.group(1) if m else f"{c.parent.name}.riddl")))
    return out

def nodes(n):
    if isinstance(n, dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)

DRIVE = {"tell-statement", "send-statement", "forward-statement"}

def census(model_dir, entry):
    p = subprocess.run([str(RIDDLC), "dump", entry.name, "--json"],
                       cwd=model_dir, capture_output=True, text=True)
    try:
        j = json.loads(p.stdout)          # stdout ALONE -- stderr is diagnostics
    except Exception as e:
        return None, f"{model_dir}: {e}"
    ns = list(nodes(j))
    ext = {n["path"] for n in ns
           if n.get("kind") == "context" and n.get("intention") == "External"}
    cmds = {}
    for n in ns:
        if n.get("kind") != "command": continue
        path = n.get("path", "")
        owner = next((e for e in ext if path.startswith(e + ".")), None)
        if owner: cmds[path] = {"id": n["id"], "ctx": owner.split(".")[-1],
                                "file": n.get("file"), "line": n["span"]["start"]["line"]}
    driven = set()
    for n in ns:
        k = n.get("kind")
        if k in DRIVE:
            r = (n.get("message") or {}).get("resolved")
            if r: driven.add(r)
        elif k == "let-statement":
            r = (n.get("declaredType") or {}).get("resolved")
            if r: driven.add(r)
    rows = [{"model": str(model_dir.relative_to(ROOT)), "cmd": p, **v}
            for p, v in sorted(cmds.items()) if p not in driven]
    return (rows, len(ext), len(cmds)), None

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows, errs, n, nctx, ncmd = [], [], 0, 0, 0
    for d, e in models():
        if only and only not in str(d): continue
        if not e.exists(): continue
        n += 1
        r, err = census(d, e)
        if err: errs.append(err)
        else:
            rs, c, m = r
            rows.extend(rs); nctx += c; ncmd += m
    # The denominator is what tells "clean" from "blind". Zero unsent commands
    # is a legitimate answer; zero external contexts never is.
    print(f"# models: {n}  external contexts: {nctx}  external commands: {ncmd}"
          f"  unsent: {len(rows)}", file=sys.stderr)
    for x in errs: print("# ERR " + x, file=sys.stderr)
    for r in rows: print(json.dumps(r))

main()
