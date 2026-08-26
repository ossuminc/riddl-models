#!/usr/bin/env python3
"""Remove a `set` that follows a `morph` in the same clause.

rc.24 (riddl a88a7df1a) makes this an Error:

    a 'set' may not follow the 'morph' at (...): the entity is in a different
    state by now, so this writes a record that is no longer current

**Deleting is safe HERE, and only because of the other rc.24 rule.** Constructors
must now supply every field, so the `morph` immediately above already builds the
complete record from the same message. The trailing `set` cannot add information
- it either restates a field the morph set, or writes prose into a record that no
longer exists.

That is why this runs AFTER scripts/fill-constructors.py and not before. Against
a partial constructor the `set` might have been carrying the only statement of a
field's value, and deleting it would lose it.

**A `set` whose value is a real record construction is HELD BACK**, not deleted:
those may carry values the morph does not, and they need a human to fold them
into the morph's constructor. Everything else here is a prose string or a
`prompt(...)` restating the transition.

Locations come from riddlc, never from a text search. The statement is deleted
from its first line through the line where its quotes balance, so a multi-line
prose string goes as one unit.

Usage:  ./scripts/drop-set-after-morph.py <model-dir> [...] [--dry-run]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOC = re.compile(r"^\[error\]\s*(?:\[[\w-]+\]\s*)?(?P<file>[^\s(]+\.riddl)\((?P<line>\d+):")


def entry_of(d):
    for c in sorted(d.glob("*.conf")):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def sites(d, entry):
    r = subprocess.run([str(RIDDLC), "--no-ansi-messages", "validate", entry],
                       cwd=d, capture_output=True, text=True)
    out, loc, found = ANSI.sub("", r.stdout + "\n" + r.stderr), None, []
    for ln in out.split("\n"):
        m = LOC.match(ln)
        if m:
            loc = (m.group("file"), int(m.group("line")))
            continue
        if loc:
            if re.match(r"a 'set' may not follow the 'morph'", ln.strip()):
                found.append(loc)
            loc = None
    return found


def main():
    dry = "--dry-run" in sys.argv
    dropped = kept = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        entry = entry_of(d)
        per_file = {}
        for fname, line in sites(d, entry):
            per_file.setdefault(fname, []).append(line)
        for fname, lns in per_file.items():
            p = (d / fname.lstrip("./")).resolve()
            lines = p.read_text().split("\n")
            drop = set()
            for n in sorted(lns, reverse=True):
                first = lines[n - 1]
                if re.search(r"set\s+(state|field)\s+[\w.]+\s+to\s+record\s", first):
                    print(f"  HOLD {arg}:{fname}:{n} constructs a record - fold it "
                          f"into the morph by hand")
                    kept += 1
                    continue
                total, j = 0, n - 1
                while j < len(lines):
                    total += lines[j].count('"')
                    drop.add(j)
                    if total % 2 == 0:
                        break
                    j += 1
                dropped += 1
            if drop and not dry:
                p.write_text("\n".join(l for i, l in enumerate(lines) if i not in drop))
    print(f"\n{dropped} statement(s) {'would be ' if dry else ''}removed, {kept} held back")


if __name__ == "__main__":
    main()
