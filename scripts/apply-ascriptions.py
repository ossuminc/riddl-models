#!/usr/bin/env python3
"""Insert the `as <shape>` ascription riddlc suggests, at the column it names.

Reads the JSONL that `collect-ascriptions.py` emits and rewrites each cited
line as

    entity Cart is {        ->  entity Cart as flow is {
    repository R is {       ->  repository R as merge is {

The grammar puts `as_shape` between the identifier and `is`
(`entity = {entity_intention} "entity" identifier [as_shape] is ...`), and
riddlc's message gives that exact point as the end column of its
`(line:start->end)` span, so no re-parsing is needed.

**Every site is checked before it is touched.** The text left of the insertion
point must end with the definition's identifier, and the text right of it must
begin with `is`. A site failing either check is reported and skipped rather
than guessed at -- a wrong column would corrupt a model silently.

Usage:
    ./scripts/apply-ascriptions.py sites.jsonl [--dry-run]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# An adaptor's header carries a direction and a context reference between the
# identifier and `is`:
#
#   adaptor = "adaptor" identifier adaptor_direction context_ref [as_shape] is
#
# riddlc's message span still ends at the identifier, so for adaptors the
# ascription belongs after the context reference, not at the reported column.
ADAPTOR_TAIL = re.compile(r"^\s+(?:to|from)\s+context\s+[\w.]+(?=\s+is\b)")


def insertion_point(line, rec):
    """Return (index, reason). `index` is a 0-based insert position, or None.

    `col` is 1-based and sits just past the identifier, which is the right spot
    for every processor kind except an adaptor -- handled explicitly rather
    than by scanning for `is`, so a malformed line is refused, not guessed at.
    """
    col = rec["col"]
    if col < 1 or col > len(line) + 1:
        return None, f"column {col} outside line of length {len(line)}"
    left, right = line[: col - 1], line[col - 1 :]
    name = rec["name"]
    # A quoted identifier keeps its quotes in the source but not in the message.
    if not (left.endswith(name) or left.endswith(f"'{name}'")):
        return None, f"text left of column does not end with {name!r}: {left!r}"
    if re.search(r"\bas\s+\w+\s+is\b", line):
        return None, "line already carries an ascription"
    if re.match(r"\s+is\b", right):
        return col - 1, ""
    tail = ADAPTOR_TAIL.match(right)
    if tail:
        return col - 1 + tail.end(), ""
    return None, f"text right of column is neither ' is' nor an adaptor tail: {right!r}"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sites = load(sys.argv[1])
    dry = "--dry-run" in sys.argv

    by_file = defaultdict(list)
    for rec in sites:
        by_file[(ROOT / rec["model"] / rec["file"])].append(rec)

    applied = skipped = 0
    problems = []
    for path, recs in sorted(by_file.items()):
        if not path.exists():
            problems.append(f"{path}: missing")
            skipped += len(recs)
            continue
        lines = path.read_text().splitlines(keepends=True)
        # Descending, so an earlier insertion never shifts a later target.
        for rec in sorted(recs, key=lambda r: (-r["line"], -r["col"])):
            idx = rec["line"] - 1
            if idx >= len(lines):
                problems.append(f"{path}:{rec['line']}: past end of file")
                skipped += 1
                continue
            raw = lines[idx]
            body = raw.rstrip("\n")
            at, why = insertion_point(body, rec)
            if at is None:
                problems.append(f"{path}:{rec['line']}: {why}")
                skipped += 1
                continue
            newline = body[:at] + f" as {rec['shape']}" + body[at:]
            lines[idx] = newline + raw[len(body) :]
            applied += 1
        if not dry:
            path.write_text("".join(lines))

    print(f"sites      : {len(sites)}")
    print(f"applied    : {applied}{'  (dry run, nothing written)' if dry else ''}")
    print(f"skipped    : {skipped}")
    for p in problems:
        print(f"  SKIP {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
