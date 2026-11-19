#!/usr/bin/env python3
"""Find `send event E(args)` that directly follows `yield event E(args')`
in the same clause where args differ; with --apply, give the send the
yield's arguments, but only when both name the same fields in the same
order and every differing send argument is a prompt."""
import re, sys, subprocess
from pathlib import Path
ROOT = Path("/Users/reid/Code/ossuminc/riddl-models")
apply = "--apply" in sys.argv

def split_args(s):
    out, d, q, cur = [], 0, False, ""
    for ch in s:
        if ch == '"': q = not q
        if not q:
            if ch in "([{": d += 1
            elif ch in ")]}": d -= 1
            elif ch == "," and d == 0:
                out.append(cur.strip()); cur = ""; continue
        cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

found = fixed = held = 0
files = subprocess.run(["git", "ls-files", "*.riddl"], cwd=ROOT, capture_output=True, text=True).stdout.split()
for f in files:
    if f.startswith("patterns/"): continue
    p = ROOT / f; lines = p.read_text().split("\n"); changed = False
    for i, l in enumerate(lines):
        m = re.match(r"(\s*)yield event ([\w.]+)\((.*)\)\s*$", l)
        if not m: continue
        ev = m.group(2).split(".")[-1]
        for j in range(i + 1, min(i + 4, len(lines))):
            n = re.match(r"(\s*send event )([\w.]+)\((.*)(\) to outlet .*)$", lines[j])
            if not (n and n.group(2).split(".")[-1] == ev): continue
            ya, sa = split_args(m.group(3)), split_args(n.group(3))
            if ya == sa: break
            found += 1
            names = lambda a: [x.split("=", 1)[0].strip() for x in a]
            ok = names(ya) == names(sa) and all(
                y == s or s.split("=", 1)[1].strip().startswith("prompt(") for y, s in zip(ya, sa))
            if ok and apply:
                lines[j] = n.group(1) + n.group(2) + "(" + ", ".join(ya) + n.group(4); changed = True; fixed += 1
            elif not ok:
                held += 1; print(f"HELD {f}:{j+1} {ev}")
            break
    if changed: p.write_text("\n".join(lines))
print(f"pairs differing: {found}, aligned: {fixed}, held: {held}")
