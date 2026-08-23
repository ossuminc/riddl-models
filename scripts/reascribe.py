#!/usr/bin/env python3
"""Correct an `as <shape>` ascription that is WRONG, using riddlc's own answer.

`apply-ascriptions.py` INSERTS an ascription where none exists; it deliberately
skips any site whose text does not read `<identifier> is`, so a site that
already carries a wrong `as <shape>` is left alone. Restructuring a processor
changes its arity, which makes existing ascriptions wrong rather than missing --
a case that script cannot reach. This is that missing counterpart.

Never derive the shape here. riddlc computes it from the arity and names it in
the error's own remediation text:

    Repository 'R' is ascribed 'as merge' but its DATAFLOW arity
      (1 outlets, 0 inlets, excluding 0 error-sink) is source:
    Suggestion: Change the ascription to 'as source', or adjust the
      inlets/outlets so the arity matches 'as merge'.

**Every site is checked before it is touched**, in the same spirit as
apply-ascriptions.py: the line must actually contain `as <the-old-shape> is`
after the named identifier, or the site is reported and skipped. A wrong
column would corrupt a model silently, and silence is the failure mode this
corpus keeps getting bitten by.

Usage:
    ./scripts/reascribe.py <model-dir> [<model-dir> ...] [--dry-run]

Exit status is 0 even when sites are skipped; read the summary.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")

# "Repository 'CartRepository' is ascribed 'as merge' but its DATAFLOW arity ... is source:"
ASCRIBED = re.compile(
    r"^\w+ '(?P<name>[\w.]+)' is ascribed 'as (?P<old>\w+)' but its DATAFLOW arity "
    r"\([^)]*\) is (?P<new>\w+):"
)
LOC = re.compile(r"^\[error\]\s*(?P<file>[^\s(]+\.riddl)\((?P<line>\d+):")


def entry_of(d):
    confs = sorted(d.glob("*.conf"))
    if confs:
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', confs[0].read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def sites(d):
    """Ask riddlc; pair each wrong-ascription error with its location."""
    r = subprocess.run(
        [str(RIDDLC), "--no-ansi-messages", "validate", entry_of(d)],
        cwd=d, capture_output=True, text=True,
    )
    out, loc, found = ANSI.sub("", r.stdout + "\n" + r.stderr), None, []
    for ln in out.split("\n"):
        m = LOC.match(ln)
        if m:
            loc = (m.group("file"), int(m.group("line")))
            continue
        if loc:
            a = ASCRIBED.match(ln.strip())
            if a:
                found.append((loc[0], loc[1], a.group("name").split(".")[-1],
                              a.group("old"), a.group("new")))
            loc = None
    return found


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    fixed = skipped = 0
    for arg in args:
        d = (ROOT / arg).resolve()
        for fname, lineno, name, old, new in sites(d):
            p = (d / fname.lstrip("./")).resolve()
            lines = p.read_text().split("\n")
            if not 1 <= lineno <= len(lines):
                print(f"SKIP {arg}:{fname}:{lineno} line out of range")
                skipped += 1
                continue
            line = lines[lineno - 1]
            # Only rewrite the ascription belonging to THIS identifier.
            pat = re.compile(rf"(\b{re.escape(name)}\s+)as\s+{re.escape(old)}\b")
            if not pat.search(line):
                print(f"SKIP {arg}:{fname}:{lineno} no 'as {old}' after '{name}':\n     {line.strip()[:120]}")
                skipped += 1
                continue
            lines[lineno - 1] = pat.sub(rf"\g<1>as {new}", line, count=1)
            print(f"{'would fix' if dry else 'fixed'} {arg}:{fname}:{lineno} {name}: as {old} -> as {new}")
            if not dry:
                p.write_text("\n".join(lines))
            fixed += 1
    print(f"\n{fixed} re-ascribed, {skipped} skipped")


if __name__ == "__main__":
    main()
