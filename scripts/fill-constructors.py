#!/usr/bin/env python3
"""Supply every field a constructor omits, using riddlc's own projection.

rc.24 (riddl commit a88a7df1a) makes a partial constructor an Error: every field
must be supplied, because an omitted field would take an invented default or
carry a stale value forward and the model states neither.

Nothing here is derived from the text. Two riddlc outputs drive it:

  riddlc dump --json   every field with its `cardinality` and `acceptsEmpty`,
                       and every on-clause with its `binding` and the resolved
                       message it handles
  riddlc validate      which constructor at which span omits which fields

The value chosen for a missing field F, in order:

  1. `F = empty`             when the field accepts it (optional, or a
                             zero-minimum collection). rc.24 checks this against
                             the declared cardinality, so a wrong guess is an
                             Error rather than a silent lie.
  2. `F = <binder>.F`        when the handled message has a field of that name --
                             the value is right there and named identically.
  3. `F = prompt("...")`     otherwise: the value genuinely is not available at
                             this point, and a typed hole is the corpus idiom
                             for that (Reid, 2026-08-23: arithmetic and derived
                             values are what the prompt is for).

Edits are applied per file in REVERSE offset order so earlier spans stay valid,
which also makes nested constructors work: the inner one is rewritten first.

The model is re-validated afterwards; if the error count did not drop, the file
is restored. A partial success is still success -- some fields need a human.

Usage:  ./scripts/fill-constructors.py <model-dir> [...] [--dry-run]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = Path(__file__).resolve().parent.parent.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOC = re.compile(r"^\[error\]\s*(?:\[[\w-]+\]\s*)?(?P<file>[^\s(]+\.riddl)\((?P<line>\d+):(?P<col>\d+)")
MISS = re.compile(r"^Constructor of (?P<kind>\w+) '(?P<name>\w+)' does not supply \d+ fields?: (?P<fields>.+?):?$")


def run(args, cwd, stdout_only=False):
    r = subprocess.run([str(RIDDLC), *args], cwd=cwd, capture_output=True, text=True)
    # `dump --json` writes the projection to stdout and its diagnostics to
    # stderr; concatenating the two makes the JSON unparseable ("Extra data").
    return ANSI.sub("", r.stdout if stdout_only else r.stdout + "\n" + r.stderr)


def entry_of(d):
    for c in sorted(d.glob("*.conf")):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def words(name):
    """`shippingCost` -> `shipping cost`, for prompt text."""
    return re.sub(r"(?<!^)(?=[A-Z])", " ", name).lower()


def projection(d, entry):
    out = run(["dump", entry, "--json"], d, stdout_only=True)
    i = out.find("[")
    nodes = json.loads(out[i:out.rfind("]") + 1]) if i >= 0 else []
    fields, clauses = {}, []
    for n in nodes:
        if n.get("kind") == "field":
            fields.setdefault(n["parent"].split(".")[-1], {})[n["id"]] = n.get("acceptsEmpty", False)
        elif n.get("kind") == "onmessageclause":
            sp = n.get("span", {})
            clauses.append((n.get("file"), sp.get("start", {}).get("line", 0),
                            sp.get("end", {}).get("line", 0), n.get("binding"),
                            (n.get("message") or {}).get("resolved", "").split(".")[-1]))
    return fields, clauses


def errors(d, entry):
    out, loc, found = run(["--no-ansi-messages", "validate", entry], d), None, []
    for ln in out.split("\n"):
        m = LOC.match(ln)
        if m:
            loc = (m.group("file"), int(m.group("line")), int(m.group("col")))
            continue
        if loc:
            mm = MISS.match(ln.strip())
            if mm:
                found.append((loc[0], loc[1], loc[2], mm.group("name"),
                              [f.strip() for f in mm.group("fields").split(",")]))
            loc = None
    return found


def close_paren(s, i):
    """Index of the `)` matching the `(` at i, ignoring parens inside strings."""
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
    return j - 1


def binder_for(clauses, fname, line):
    """Innermost on-clause containing this line."""
    best = None
    for f, a, b, binding, msg in clauses:
        if f and Path(f).name == Path(fname).name and a <= line <= b:
            if best is None or a > best[0]:
                best = (a, binding, msg)
    return (best[1], best[2]) if best else (None, None)


def main():
    dry = "--dry-run" in sys.argv
    total = held = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        entry = entry_of(d)
        fields, clauses = projection(d, entry)
        errs = errors(d, entry)
        if not errs:
            continue
        before = len(errs)
        per_file = {}
        for fname, line, col, tname, missing in errs:
            per_file.setdefault(fname, []).append((line, col, tname, missing))
        changed = {}
        for fname, items in per_file.items():
            p = (d / fname.lstrip("./")).resolve()
            src = p.read_text()
            lines = src.split("\n")
            offs, acc = [], 0
            for L in lines:
                offs.append(acc)
                acc += len(L) + 1
            edits = []
            for line, col, tname, missing in items:
                base = offs[line - 1]
                open_at = src.find(f"{tname}(", base + col - 1)
                if open_at < 0:
                    open_at = src.find(f"{tname}(", base)
                if open_at < 0:
                    print(f"  SKIP {arg}:{fname}:{line} cannot locate {tname}( ")
                    held += 1
                    continue
                lp = open_at + len(tname)
                rp = close_paren(src, lp)
                binder, msg = binder_for(clauses, fname, line)
                known = fields.get(msg, {}) if msg else {}
                add = []
                for f in missing:
                    if fields.get(tname, {}).get(f):
                        add.append(f"{f} = empty")
                    elif binder and f in known:
                        add.append(f"{f} = {binder}.{f}")
                    else:
                        add.append(f'{f} = prompt("the {words(f)} of this {words(tname)}")')
                inner = src[lp + 1:rp].strip()
                sep = ", " if inner else ""
                edits.append((rp, sep + ", ".join(add)))
            for at, text in sorted(edits, key=lambda e: -e[0]):
                src = src[:at] + text + src[at:]
            changed[p] = src
            total += len(edits)
        if dry:
            continue
        backup = {p: p.read_text() for p in changed}
        for p, s in changed.items():
            p.write_text(s)
        after = len(errors(d, entry))
        if after >= before:
            for p, s in backup.items():
                p.write_text(s)
            print(f"  REVERTED {arg}: {before} -> {after} errors, no improvement")
        else:
            print(f"  {arg}: {before} -> {after} constructor errors")
    print(f"\n{total} field(s) {'would be ' if dry else ''}supplied, {held} site(s) held back")


if __name__ == "__main__":
    main()
