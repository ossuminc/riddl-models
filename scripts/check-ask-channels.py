#!/usr/bin/env python3
"""GUARD: every `ask` must have a channel. riddlc does not check this.

`ask query Q of <target>` is `send` plus a declared correlation (Reid,
2026-09-09): the request travels a connector like any other message. riddlc
enforces only `msg-ask-not-handled` -- that the target declares `on query Q` --
and checks neither an admitting portlet nor reachability, though it checks BOTH
for `tell`. A clean `riddlc validate` is therefore NOT evidence that an `ask`
is connected, and that silence already taught this repository the wrong rule
once. See ../riddl/task/2026-09-09-ask-is-not-checked-for-a-channel.md.

This stands in for the missing checks until they land upstream:

  1. the target declares an inlet whose type IS the query, or whose alternation
     contains it
  2. a connector reaches that inlet from the asking processor, or from
     somewhere inside it

Usage:  ./scripts/check-ask-channels.py [model-substring]
Exit 1 on any unchannelled ask.
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = _r if os.path.isabs(_r) else str((ROOT / _r).resolve())
ASK = re.compile(r"^\s*ask\s+query\s+([\w.]+)\s+of\s+(?:\w+\s+)?([\w.]+)\s*$")


def nodes(n):
    if isinstance(n, dict):
        if n.get("kind"): yield n
        for v in n.values(): yield from nodes(v)
    elif isinstance(n, list):
        for v in n: yield from nodes(v)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    asks = bad = models = 0
    for conf in sorted(ROOT.rglob("*.conf")):
        if "patterns" in conf.relative_to(ROOT).parts: continue
        d = conf.parent
        if only and only not in str(d): continue
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', conf.read_text())
        e = d / (m.group(1) if m else f"{d.name}.riddl")
        if not e.exists(): continue
        p = subprocess.run([RIDDLC, "dump", e.name, "--json"], cwd=d,
                           capture_output=True, text=True)
        try: j = json.loads(p.stdout)
        except Exception:
            print(f"FAIL {d.relative_to(ROOT)}: dump did not parse"); bad += 1; continue
        ns = list(nodes(j)); models += 1
        inlets = [n for n in ns if n.get("kind") == "inlet"]
        conns = [n for n in ns if n.get("kind") == "connector"]
        paths = {n["path"] for n in ns if n.get("path")}
        for n in ns:
            if n.get("kind") != "let-statement": continue
            v = (n.get("value") or {}).get("value") or ""
            mm = ASK.match(v)
            if not mm: continue
            asks += 1
            qref, tref = mm.group(1), mm.group(2)
            # resolve by suffix against the model's own resolved paths
            q = next((x for x in paths if x.endswith("." + qref) or x == qref), None)
            t = next((x for x in paths if x.endswith("." + tref) or x == tref), None)
            where = f"{d.relative_to(ROOT)} {n['file']}:{n['span']['start']['line']}"
            if not q or not t:
                print(f"FAIL {where}: cannot resolve `{v}`"); bad += 1; continue
            admitting = []
            for il in inlets:
                if il.get("parent") != t: continue
                ty = il.get("type") or {}
                alts = [a.get("resolved") for a in (ty.get("alternation") or [])]
                if ty.get("resolved") == q or q in alts: admitting.append(il["path"])
            if not admitting:
                print(f"FAIL {where}: {t.split('.')[-1]} has no inlet admitting "
                      f"{q.split('.')[-1]}"); bad += 1; continue
            asker = n.get("ancestors", [])[-1]
            reached = False
            for c in conns:
                to = (c.get("to") or {}).get("resolved")
                fr = (c.get("from") or {}).get("resolved") or ""
                if to in admitting and any(fr == a or fr.startswith(a + ".")
                                           for a in n.get("ancestors", [])):
                    reached = True; break
            if not reached:
                print(f"FAIL {where}: no connector reaches "
                      f"{admitting[0].split('.')[-1]} from the asker"); bad += 1
    print(f"\nchecked {models} models, {asks} `ask` statements, {bad} unchannelled")
    if asks == 0 and not only:
        sys.exit("no `ask` statements found at all -- the check measured nothing")
    sys.exit(1 if bad else 0)


main()
