#!/usr/bin/env python3
"""Repair a generated `Persist<E>(...)` constructor that names the wrong field.

The campaign generated each projector clause as

    tell command <Ctx>.<Repo>.Persist<E>(<id> = <binder>.<id>) to repository ...

guessing <id> from the event's FIRST field. That guess is wrong wherever the
first field is not the identity: `AdjusterAssigned` leads with `adjusterId` and
`ClaimDenied` with `denialReason`, while both Persist commands want `claimId`.
Elsewhere the guess simply used a different spelling than the declaration
(`batchId` where both the event and the command say `drugBatchId`).

Both produce a PAIR of errors per site -- one for the field not existing on the
command, one for the value reference not resolving on the event.

The correct name is not derived here. riddlc names it in its own remediation
text, exactly as it does for ascriptions:

    'batchId' is not a field of Command 'PersistBatchManufactured':
    Suggestion: Use one of the fields of Command 'PersistBatchManufactured': drugBatchId.

That field is then used on BOTH sides -- `F = <binder>.F` -- because the Persist
command's id field is generated from the event's, so the event carries the same
name. Where it does not, riddlc says so on the next run and the site is left for
hand work rather than being silently mangled.

Only rewrites when the suggestion names EXACTLY ONE field, and only when the
cited line actually contains the bad `<field> = <binder>.<something>` pair.
Anything else is reported and skipped.

Usage:  ./scripts/fix-persist-fields.py <model-dir> [...] [--dry-run]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOC = re.compile(r"^\[error\]\s*(?:\[[\w-]+\]\s*)?(?P<file>[^\s(]+\.riddl)\((?P<line>\d+):")
BAD = re.compile(r"^'(?P<bad>\w+)' is not a field of Command '(?P<cmd>\w+)':")
SUG = re.compile(r"^Suggestion:\s*Use one of the fields of Command '\w+':\s*(?P<fields>.+?)\.?\s*$")


def entry_of(d):
    confs = sorted(d.glob("*.conf"))
    if confs:
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', confs[0].read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def sites(d):
    # --provide-tips is what makes riddlc print the "Suggestion:" line at all;
    # without it the remediation text this script depends on simply is not there.
    r = subprocess.run([str(RIDDLC), "--provide-tips", "--no-ansi-messages",
                        "validate", entry_of(d)],
                       cwd=d, capture_output=True, text=True)
    lines = ANSI.sub("", r.stdout + "\n" + r.stderr).split("\n")
    found, loc, bad = [], None, None
    for ln in lines:
        m = LOC.match(ln)
        if m:
            loc, bad = (m.group("file"), int(m.group("line"))), None
            continue
        if loc and bad is None:
            b = BAD.match(ln.strip())
            if b:
                bad = b.groupdict()
                continue
            loc = None
        elif loc and bad is not None:
            # The echoed source line sits between the message and its Suggestion,
            # so keep scanning rather than discarding the pending record here.
            s = SUG.match(ln.strip())
            if s:
                found.append((loc[0], loc[1], bad["bad"], bad["cmd"],
                              [f.strip() for f in s.group("fields").split(",")]))
                loc, bad = None, None
    return found


def main():
    dry = "--dry-run" in sys.argv
    fixed = skipped = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        for fname, lineno, bad, cmd, fields in sites(d):
            if len(fields) != 1:
                print(f"SKIP {arg}:{fname}:{lineno} {cmd}: {len(fields)} candidate fields {fields}")
                skipped += 1
                continue
            good = fields[0]
            p = (d / fname.lstrip("./")).resolve()
            lines = p.read_text().split("\n")
            line = lines[lineno - 1]
            pat = re.compile(rf"\b{re.escape(bad)}\s*=\s*(\w+)\.\w+")
            m = pat.search(line)
            if not m:
                print(f"SKIP {arg}:{fname}:{lineno} {cmd}: no '{bad} = <binder>.<field>' on line")
                skipped += 1
                continue
            lines[lineno - 1] = pat.sub(f"{good} = {m.group(1)}.{good}", line, count=1)
            print(f"{'would fix' if dry else 'fixed'} {arg}:{fname}:{lineno} "
                  f"{cmd}: {bad} -> {good}")
            if not dry:
                p.write_text("\n".join(lines))
            fixed += 1
    print(f"\n{fixed} constructors {'would be ' if dry else ''}repaired, {skipped} skipped")


if __name__ == "__main__":
    main()
