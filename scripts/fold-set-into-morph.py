#!/usr/bin/env python3
"""Fold a `set ... to record ...` into the `morph` above it, then remove it.

The remaining half of rc.24's `set`-after-`morph` rule. riddlc's own remediation:

    Move these values into the 'morph' statement's own record constructor, or
    handle them in an `on` clause of the state being morphed TO.

These sites are NOT redundant - the two constructors disagree - so they cannot
just be deleted the way the prose ones were. In MenuItem the `set` supplies
`menuItemLifecycle = DraftLifecycle`, a concrete value, where the morph carries
`MenuItemStateData.menuItemLifecycle` forward from a state that does not exist
yet at creation. The morph in turn has `menuItemCreatedAt` from the event where
the `set` only has `prompt("current timestamp")`.

So the merge is per FIELD, keeping the better-founded value. The ranking, best
first, and it is about where a value comes FROM rather than what it looks like:

  3  a field of the handled message      `menuItemCreated.menuItemCreatedAt`
  2  a literal or named value            `DraftLifecycle`, `empty`, `"text"`
  1  a typed hole                        `prompt("current timestamp")`
  0  carried forward from the state      `MenuItemStateData.menuItemLifecycle`
     record being CONSTRUCTED -- self-referential, and on a creation transition
     it names a record that does not exist yet

Ties keep the morph's value: it is the statement that survives, and preferring
the incumbent means a tie never rewrites anything.

Locations come from riddlc. The model is re-validated and restored if the error
count does not drop.

Usage:  ./scripts/fold-set-into-morph.py <model-dir> [...] [--dry-run]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOC = re.compile(r"^\[error\]\s*(?P<file>[^\s(]+\.riddl)\((?P<line>\d+):")


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


def sites(d, entry):
    out, loc, found = validate(d, entry), None, []
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


def arglist(s):
    """(open_index, close_index, {field: value}) for the first `(` in s."""
    i = s.index("(")
    d, j, q = 1, i + 1, False
    while j < len(s) and d:
        c = s[j]
        if q:
            q = c != '"'
        elif c == '"':
            q = True
        elif c == "(":
            d += 1
        elif c == ")":
            d -= 1
        j += 1
    body = s[i + 1:j - 1]
    args, depth, cur, q = {}, 0, "", False
    parts = []
    for c in body:
        if q:
            q = c != '"'
        elif c == '"':
            q = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == "," and depth == 0 and not q:
            parts.append(cur)
            cur = ""
            continue
        cur += c
    if cur.strip():
        parts.append(cur)
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            args[k.strip()] = v.strip()
    return i, j - 1, args


def rank(value, record):
    if value.startswith("prompt("):
        return 1
    if re.match(rf"{re.escape(record)}\.\w+$", value):
        return 0
    if re.match(r"\w+\.\w+$", value):
        return 3
    return 2


def main():
    dry = "--dry-run" in sys.argv
    folded = skipped = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        entry = entry_of(d)
        found = sites(d, entry)
        if not found:
            continue
        before = validate(d, entry).count("may not follow")
        per_file = {}
        for fname, line in found:
            per_file.setdefault(fname, []).append(line)
        touched = {}
        for fname, lns in per_file.items():
            p = (d / fname.lstrip("./")).resolve()
            lines = p.read_text().split("\n")
            backup = list(lines)
            drop = set()
            for n in sorted(lns, reverse=True):
                setline = lines[n - 1]
                if "to record " not in setline:
                    continue
                # The morph is not always the previous line -- a multi-line
                # `do "..."` often sits between. Scan back within the clause,
                # stopping at its opening `on ... is {`.
                mi = None
                for b in range(n - 2, max(-1, n - 16), -1):
                    if re.match(r"\s*on \w+.*\bis\s*\{", lines[b]):
                        break
                    if "morph " in lines[b] and "(" in lines[b]:
                        mi = b
                        break
                if mi is None:
                    print(f"  SKIP {arg}:{fname}:{n} no morph found in this clause")
                    skipped += 1
                    continue
                mline = lines[mi]
                try:
                    mo, mc, margs = arglist(mline)
                    _, _, sargs = arglist(setline[setline.index("to record "):])
                except ValueError:
                    print(f"  SKIP {arg}:{fname}:{n} could not read both constructors")
                    skipped += 1
                    continue
                rec = re.search(r"record\s+[\w.]*?(\w+)\(", mline)
                rec = rec.group(1) if rec else ""
                merged = dict(margs)
                for k, v in sargs.items():
                    if k in merged and rank(v, rec) > rank(merged[k], rec):
                        merged[k] = v
                    elif k not in merged:
                        merged[k] = v
                body = ", ".join(f"{k} = {v}" for k, v in merged.items())
                lines[mi] = mline[:mo + 1] + body + mline[mc:]
                drop.add(n - 1)
                folded += 1
            if drop:
                lines = [l for i, l in enumerate(lines) if i not in drop]
                touched[p] = ("\n".join(lines), "\n".join(backup))
        if dry or not touched:
            continue
        for p, (new, _) in touched.items():
            p.write_text(new)
        after = validate(d, entry).count("may not follow")
        if after >= before:
            for p, (_, old) in touched.items():
                p.write_text(old)
            print(f"  REVERTED {arg}: {before} -> {after}")
        else:
            print(f"  {arg}: {before} -> {after} set-after-morph")
    print(f"\n{folded} folded, {skipped} skipped")


if __name__ == "__main__":
    main()
