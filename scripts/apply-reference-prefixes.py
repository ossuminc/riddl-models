#!/usr/bin/env python3
"""Rewrite a reference's `type` prefix to the target's DECLARED kind.

riddlc 2.0.0-rc.24-5 makes it an Error for a reference to prefix with `type`
something declared a command, query, event, result or record:

    inlet OrderResultOut is type Order.OrderResult
                            ^^^^ declared a result

The diagnostic names both sides, so the correct word is riddlc's, not ours:

    'Order.OrderResult' is declared a result, but this reference names it as
    a type:  Suggestion: Write 'result Order.OrderResult'. ...

Reads the JSONL that `collect-warnings.py` emits and replaces the `type`
keyword at the START of each cited span. Only that one token is touched -- the
span's tail may run onto the next line, and never needs to be read.

**Every site is checked before it is touched.** The word at the cited column
must be exactly `type` followed by whitespace, and the kind parsed from the
message must be one riddlc could have declared. A site failing either check is
reported and SKIPPED rather than guessed at; a wrong column would corrupt a
model silently and `sbt v` would not necessarily say so.

Edits are applied per file from the bottom up, so an earlier rewrite never
shifts the column of a later one.

Usage:
    ./scripts/collect-warnings.py > sites.jsonl
    ./scripts/apply-reference-prefixes.py sites.jsonl [--dry-run]
"""
import json
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The kinds an `aggregate_use_case` prefix may name (ebnf-grammar.ebnf:115).
KINDS = {"command", "query", "event", "result", "record", "graph", "table", "type"}

MSG = re.compile(r"is declared a (\w+), but this reference names it as a type")


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    positional = [a for a in argv if not a.startswith("--")]
    if not positional:
        sys.exit(__doc__)
    recs = load(positional[0])

    by_file = defaultdict(list)
    skipped = []
    for r in recs:
        m = MSG.search(r.get("message", ""))
        if not m:
            continue  # not our rule; collect-warnings reports everything
        kind = m.group(1)
        if kind not in KINDS:
            skipped.append((r, f"unknown declared kind {kind!r}"))
            continue
        by_file[(r["model"], r["file"])].append((r, kind))

    applied = Counter()
    for (model, fname), sites in sorted(by_file.items()):
        path = ROOT / model / fname
        if not path.is_file():
            skipped.extend((r, f"no such file {path}") for r, _ in sites)
            continue
        lines = path.read_text().split("\n")
        # Bottom-up: a rewrite lengthens its line, so later columns on the
        # same line must be done first.
        for r, kind in sorted(sites, key=lambda s: (s[0]["line"], s[0]["col"]), reverse=True):
            i, c = r["line"] - 1, r["col"] - 1
            if i >= len(lines):
                skipped.append((r, "line past end of file"))
                continue
            line = lines[i]
            if not re.match(r"type\s", line[c:]):
                skipped.append((r, f"expected 'type' at col {r['col']}, found {line[c:c+12]!r}"))
                continue
            lines[i] = line[:c] + kind + line[c + len("type"):]
            applied[kind] += 1
        if not dry:
            path.write_text("\n".join(lines))

    total = sum(applied.values())
    verb = "would rewrite" if dry else "rewrote"
    print(f"{verb} {total} references across {len(by_file)} files:")
    for kind, n in applied.most_common():
        print(f"  {n:5d}  type -> {kind}")
    if skipped:
        print(f"\nSKIPPED {len(skipped)} site(s) rather than guess:")
        for r, why in skipped[:20]:
            print(f"  {r['model']}/{r['file']}:{r['line']}:{r['col']}  {why}")
        if len(skipped) > 20:
            print(f"  ... and {len(skipped) - 20} more")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
