#!/usr/bin/env python3
"""Collect every 'as <shape>' ascription riddlc suggests, for the whole corpus.

riddlc knows the answer: `validateProcessorShape` derives the shape from the
processor's arity and attaches it to the style warning as a remediation
suggestion, which `--provide-tips` prints. Deriving it here instead would mean
reimplementing `shapeForArity` and keeping it in step -- so this asks the
compiler rather than guessing.

Emits one JSON record per site to stdout:

    {"model": ..., "file": ..., "line": N, "col": N,
     "kind": "Entity", "name": "Cart", "shape": "flow"}

`col` is the 1-based column just past the identifier -- the exact point where
` as <shape>` belongs, taken from riddlc's own `(line:startcol->endcol)`.

Usage:
    ./scripts/collect-ascriptions.py [limit] [--include-patterns]

`--include-patterns` adds the two `patterns/` examples, which `riddlcValidate`
excludes but the test suite checks -- they account for 6 of the sites.
Set RIDDLC=... to override the binary.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = Path(os.environ.get("RIDDLC", ROOT.parent / "bin" / "riddlc"))

# "[style] CartContext.riddl(142:3->28):" -- the severity prefix is always
# present in riddlc's formatted output, so it is stripped here rather than
# assumed away.
LOC = re.compile(
    r"^(?:\[\w+\]\s*)?(?P<file>[^\s(]+\.riddl)"
    r"\((?P<line>\d+):(?P<c1>\d+)->(?P<c2>\d+)\):$"
)
# "Repository 'CartRepository' has ports but no 'as <shape>' ascription"
WARN = re.compile(r"^(?P<kind>\w[\w -]*) '(?P<name>[^']+)' has ports but no 'as <shape>' ascription")
# "Suggestion: Add 'as merge' to Repository 'CartRepository' to document ..."
SUGG = re.compile(r"^Suggestion: Add 'as (?P<shape>\w+)' to (?P<kind>\w[\w -]*) '(?P<name>[^']+)'")


INPUT_FILE = re.compile(r'^\s*input-file\s*=\s*"?([^"\s]+)"?', re.MULTILINE)


def entry_file(conf):
    """The model's entry point, per the .conf's `input-file`.

    Most models name it after their directory, but the pattern examples do not
    (`example.riddl` in `patterns/entity/*/`), so the .conf is read rather than
    the convention assumed.
    """
    m = INPUT_FILE.search(conf.read_text())
    if m:
        return conf.parent / m.group(1)
    return conf.parent / f"{conf.parent.name}.riddl"


def models(include_patterns=False):
    confs = sorted(
        p for p in ROOT.rglob("*.conf")
        if include_patterns or "patterns" not in p.relative_to(ROOT).parts
    )
    return [(c.parent, entry_file(c)) for c in confs]


def collect(model_dir, entry):
    """Run riddlc on one model, pairing each warning with its suggestion."""
    if not entry.exists():
        return []
    proc = subprocess.run(
        [str(RIDDLC), "--provide-tips", "--no-ansi-messages",
         "validate", entry.name],
        cwd=model_dir, capture_output=True, text=True,
    )
    out = []
    lines = proc.stdout.splitlines() + proc.stderr.splitlines()
    pending = None  # (file, line, col) of the most recent location header
    warned = None   # (kind, name) awaiting its Suggestion line
    for raw in lines:
        s = raw.strip()
        m = LOC.match(s)
        if m:
            pending = (m.group("file"), int(m.group("line")), int(m.group("c2")))
            warned = None
            continue
        m = WARN.match(s)
        if m and pending:
            warned = (m.group("kind"), m.group("name"))
            continue
        m = SUGG.match(s)
        if m and warned and pending:
            # The suggestion must name the same definition as the warning, or
            # the two lines belong to different messages and pairing them would
            # write the wrong shape into the wrong place.
            if (m.group("kind"), m.group("name")) == warned:
                out.append({
                    "model": str(model_dir.relative_to(ROOT)),
                    "file": pending[0], "line": pending[1], "col": pending[2],
                    "kind": warned[0], "name": warned[1], "shape": m.group("shape"),
                })
            warned = None
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dirs = models(include_patterns="--include-patterns" in sys.argv)
    if args:
        dirs = dirs[: int(args[0])]
    if not RIDDLC.is_file() or not os.access(RIDDLC, os.X_OK):
        sys.exit(f"riddlc not found/executable at {RIDDLC}")
    for d, entry in dirs:
        for rec in collect(d, entry):
            print(json.dumps(rec))


if __name__ == "__main__":
    main()
