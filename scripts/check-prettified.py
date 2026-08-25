#!/usr/bin/env python3
"""Fail if any model is not in `riddlc prettify` canonical form.

Nothing else in the build sees formatting. `sbt v`, `collect-warnings.py` and
the test suite all report a corpus as clean while its text drifts arbitrarily
far from what prettify emits -- which is how 188 of 188 models came to differ
in 396 files (BACKLOG #26) without a single gate noticing.

That matters because `scripts/verify-bast-roundtrip.sh` compares the
unbastified tree against the source BYTE FOR BYTE, and that comparison is only
meaningful while the source IS what prettify emits. Drift does not make the
round-trip check fail loudly and honestly; it makes it fail for a reason that
has nothing to do with the `.bast` files it is supposedly checking.

So: run `sbt r` before committing model edits. This task is what enforces it.

`patterns/` is excluded, matching `riddlcConfExclusions` and
`verify-bast-roundtrip.sh`. Its examples diverge from canonical form
DELIBERATELY (BACKLOG #3): they are documentation, and canonicalising them
would emit 341-character alternations and two ports per line.

Usage:
    ./scripts/check-prettified.py [limit] [--diff]

`--diff` prints the first differing lines per file. Set RIDDLC=... to override
the binary; a relative value resolves against the repository root.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_riddlc = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_riddlc) if os.path.isabs(_riddlc) else (ROOT / _riddlc).resolve()

INPUT_FILE = re.compile(r'input-file\s*=\s*"([^"]+)"')


def entry_file(conf):
    m = INPUT_FILE.search(conf.read_text())
    return conf.parent / m.group(1) if m else conf.with_suffix(".riddl")


def models():
    return [
        (c.parent, entry_file(c))
        for c in sorted(ROOT.rglob("*.conf"))
        if "patterns" not in c.relative_to(ROOT).parts
    ]


def main():
    argv = sys.argv[1:]
    show = "--diff" in argv
    positional = [a for a in argv if not a.startswith("--")]
    if not RIDDLC.is_file() or not os.access(RIDDLC, os.X_OK):
        sys.exit(f"riddlc not found/executable at {RIDDLC}")

    dirs = models()
    if positional:
        dirs = dirs[: int(positional[0])]

    drifted, checked, errors = [], 0, []
    with tempfile.TemporaryDirectory() as tmp:
        for d, entry in dirs:
            if not entry.exists():
                errors.append((d, "entry file missing"))
                continue
            out = Path(tmp) / str(d.relative_to(ROOT)).replace("/", "_")
            p = subprocess.run(
                [str(RIDDLC), "prettify", entry.name, "-o", str(out)],
                cwd=d, capture_output=True, text=True,
            )
            if p.returncode != 0:
                errors.append((d, (p.stderr or p.stdout).strip()[-200:]))
                continue
            for got in sorted(out.rglob("*.riddl")):
                src = d / got.relative_to(out)
                checked += 1
                if not src.exists():
                    drifted.append((src, "produced by prettify but absent from the tree"))
                elif src.read_bytes() != got.read_bytes():
                    # keep the TEXT, not the path: the temp dir is gone by the
                    # time the report below runs
                    drifted.append((src, got.read_text()))

    rel = lambda p: str(Path(p).relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p)

    if errors:
        print(f"prettify FAILED to run on {len(errors)} model(s):")
        for d, why in errors[:10]:
            print(f"  {rel(d)}: {why}")
        return 2

    if drifted:
        print(f"{len(drifted)} of {checked} .riddl file(s) are NOT in canonical form:\n")
        for src, got in drifted[:40]:
            print(f"  {rel(src)}")
            if show and isinstance(got, str):
                a = src.read_text().split("\n")
                b = got.split("\n")
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        print(f"      line {i+1}\n        is: {x[:100]}\n      want: {y[:100]}")
                        break
        if len(drifted) > 40:
            print(f"  ... and {len(drifted) - 40} more")
        print("\nRun `sbt r` (riddlcPrettify) and commit the result.")
        return 1

    print(f"all {checked} .riddl files across {len(dirs)} models are in canonical form")
    return 0


if __name__ == "__main__":
    sys.exit(main())
