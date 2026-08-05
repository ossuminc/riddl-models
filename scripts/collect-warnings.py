#!/usr/bin/env python3
"""Dump every riddlc message for the corpus as JSONL, with location and tip.

A general companion to `collect-ascriptions.py`: where that one harvests a
single warning class it knows how to fix, this one reports everything, so a
class of warning can be surveyed before deciding what to do about it.

Each record:

    {"model": ..., "file": ..., "line": N, "col": N, "endcol": N,
     "level": "style", "message": "...", "suggestion": "..."}

Usage:
    ./scripts/collect-warnings.py [limit] [--include-patterns] [--grep TEXT]

`--grep` keeps only messages containing TEXT. Set RIDDLC=... to override the
binary; a relative value is resolved against the repository root, since this
script changes directory per model.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_riddlc = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_riddlc) if os.path.isabs(_riddlc) else (ROOT / _riddlc).resolve()

LOC = re.compile(
    r"^\[(?P<level>\w+)\]\s*(?P<file>[^\s(]+\.riddl)"
    r"\((?P<line>\d+):(?P<c1>\d+)(?:->(?P<c2>\d+))?\):$"
)
SUGG = re.compile(r"^Suggestion:\s*(?P<tip>.+)$")
INPUT_FILE = re.compile(r'^\s*input-file\s*=\s*"?([^"\s]+)"?', re.MULTILINE)


def entry_file(conf):
    m = INPUT_FILE.search(conf.read_text())
    return conf.parent / (m.group(1) if m else f"{conf.parent.name}.riddl")


def models(include_patterns=False):
    confs = sorted(
        p for p in ROOT.rglob("*.conf")
        if include_patterns or "patterns" not in p.relative_to(ROOT).parts
    )
    return [(c.parent, entry_file(c)) for c in confs]


def collect(model_dir, entry):
    if not entry.exists():
        return []
    proc = subprocess.run(
        [str(RIDDLC), "--provide-tips", "--no-ansi-messages", "validate", entry.name],
        cwd=model_dir, capture_output=True, text=True,
    )
    out, cur = [], None
    for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
        s = raw.strip()
        m = LOC.match(s)
        if m:
            cur = {
                "model": str(model_dir.relative_to(ROOT)),
                "file": m.group("file"),
                "line": int(m.group("line")),
                "col": int(m.group("c1")),
                "endcol": int(m.group("c2") or m.group("c1")),
                "level": m.group("level"),
                "message": "",
                "suggestion": "",
            }
            out.append(cur)
            continue
        if cur is None or not s:
            continue
        m = SUGG.match(s)
        if m:
            cur["suggestion"] = m.group("tip")
            cur = None
        elif not cur["message"]:
            cur["message"] = s
    return out


def main():
    argv = sys.argv[1:]
    grep = None
    if "--grep" in argv:
        i = argv.index("--grep")
        grep = argv[i + 1]
        del argv[i : i + 2]
    positional = [a for a in argv if not a.startswith("--")]
    dirs = models(include_patterns="--include-patterns" in argv)
    if positional:
        dirs = dirs[: int(positional[0])]
    if not RIDDLC.is_file() or not os.access(RIDDLC, os.X_OK):
        sys.exit(f"riddlc not found/executable at {RIDDLC}")
    for d, entry in dirs:
        for rec in collect(d, entry):
            if grep and grep not in rec["message"]:
                continue
            print(json.dumps(rec))


if __name__ == "__main__":
    main()
