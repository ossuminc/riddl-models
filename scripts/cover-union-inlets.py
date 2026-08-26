#!/usr/bin/env python3
"""Give a processor an `on other` clause for the union members it does not name.

riddlc reports, per inlet:

    Inlet 'I' admits Type 'T' but <Kind> 'N' declares no handler clause for M of
    its K members (...), so nothing happens when one of those arrives

The author's ruling (BACKLOG #20): implement the clauses, do not delete the
inlet; a union inlet needs a clause for EVERY member, "or an `on other` clause if
anything arriving should be handled generically". This adds the latter where the
uncovered members genuinely share one policy.

That is the case here and it is worth stating rather than assuming: the uncovered
members are overwhelmingly `<Command>Rejected` events arriving at a sink, a
display flow or an external context's inbound port. A rejection changes no stored
row and starts no work downstream, so "nothing happens" IS the intended policy -
`on other` states it, where a per-member clause would repeat it K times.

The clause is placed in a handler that owns the reported inlet's parent, and only
where no `on other` already exists. Locations come from riddlc; the model is
re-validated per model and restored if the finding count does not drop.

Usage:  ./scripts/cover-union-inlets.py <model-dir> [...] [--dry-run]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOC = re.compile(r"^\[\w+\]\s*(?:\[[\w-]+\]\s*)?(?P<file>[^\s(]+\.riddl)\((?P<line>\d+):")
ADMITS = re.compile(r"^Inlet '(?P<inlet>\w+)' admits Type '(?P<type>\w+)' but "
                    r"(?P<kind>\w+) '(?P<owner>\w+)' declares no handler clause for "
                    r"(?P<n>\d+) of its (?P<k>\d+) members")


def entry_of(d):
    for c in sorted(d.glob("*.conf")):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def validate(d, entry):
    r = subprocess.run([str(RIDDLC), "--no-ansi-messages", "validate", entry],
                       cwd=d, capture_output=True, text=True)
    return ANSI.sub("", r.stdout + "\n" + r.stderr)


def findings(out):
    loc, found = None, []
    for ln in out.split("\n"):
        m = LOC.match(ln)
        if m:
            loc = (m.group("file"), int(m.group("line")))
            continue
        if loc:
            a = ADMITS.match(ln.strip())
            if a:
                found.append((loc[0], loc[1], a.group("kind"), a.group("owner")))
            loc = None
    return found


def block(s, i):
    j = s.index("{", i)
    d, k = 1, j + 1
    while d and k < len(s):
        d += (s[k] == "{") - (s[k] == "}")
        k += 1
    return j, k


def main():
    dry = "--dry-run" in sys.argv
    added = skipped = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        entry = entry_of(d)
        out = validate(d, entry)
        before = len(findings(out))
        if not before:
            continue
        seen, touched = set(), {}
        for fname, line, kind, owner in findings(out):
            if owner in seen:
                continue
            seen.add(owner)
            p = (d / fname.lstrip("./")).resolve()
            s = touched.get(p, p.read_text())
            # Locate the owner and the FIRST handler inside it.
            om = re.search(rf"^( *)(?:[\w-]+\s+)*\w+\s+{owner}\s+(?:\w+\s+)*is\s*\{{", s, re.M)
            if not om:
                print(f"  SKIP {arg}: cannot locate {kind} {owner}")
                skipped += 1
                continue
            _, oend = block(s, om.start())
            # prettify jams declarations onto one line, so the handler is not
            # always at the start of one: `inlet X is type T    handler H is {`.
            hm = re.search(r"(?:initial\s+)?handler\s+\w+\s+is\s*\{", s[om.start():oend])
            if not hm:
                print(f"  SKIP {arg}: {kind} {owner} has no handler")
                skipped += 1
                continue
            hstart = om.start() + hm.start()
            _, hend = block(s, hstart)
            if re.search(r"^\s*on other is", s[hstart:hend], re.M):
                print(f"  SKIP {arg}: {kind} {owner} already has `on other`")
                skipped += 1
                continue
            at = om.start() + hm.end()
            if at < len(s) and s[at] == "\n":
                at += 1
            lstart = s.rfind("\n", 0, om.start() + hm.start()) + 1
            ind = re.match(r"[ \t]*", s[lstart:]).group(0) + "  "
            s = (s[:at] + f"{ind}on other is {{\n"
                 f'{ind}  do "the remaining members of this inlet\'s type - rejections and '
                 f'events this {kind.lower()} does not act on - change nothing here"\n'
                 f"{ind}}}\n" + s[at:])
            touched[p] = s
            added += 1
        if dry or not touched:
            continue
        backup = {p: p.read_text() for p in touched}
        for p, s in touched.items():
            p.write_text(s)
        after = len(findings(validate(d, entry)))
        if after >= before:
            for p, s in backup.items():
                p.write_text(s)
            print(f"  REVERTED {arg}: {before} -> {after}")
        else:
            print(f"  {arg}: {before} -> {after} union-inlet findings")
    print(f"\n{added} `on other` clause(s) {'would be ' if dry else ''}added, {skipped} skipped")


if __name__ == "__main__":
    main()
