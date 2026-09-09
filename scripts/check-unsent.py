#!/usr/bin/env python3
"""RATCHET: no model may gain a command that nothing drives.

An external context's command that nothing tells or sends is a wiring gap --
riddlc has no opinion about an unsent message, so nothing else in this build
sees one.  BACKLOG #33 is the campaign to close them; this stops the number
growing while that runs.

The baseline (`scripts/unsent-baseline.tsv`, tracked) lists every known gap.
The check fails on any gap NOT in it.  Gaps that have been closed are
reported, and refreshing the baseline is how the ratchet tightens:

    ./scripts/check-unsent.py --update

Set RIDDLC=... to override the binary; a relative value resolves against the
repository root, since the census changes directory per model.
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "unsent-baseline.tsv"
CENSUS = ROOT / "scripts" / "adaptor-wiring" / "census.py"


def current():
    p = subprocess.run([sys.executable, str(CENSUS)], cwd=ROOT,
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"census failed:\n{p.stderr}")
    import json, re
    rows = [json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    # ZERO FINDINGS IS NOW THE TRUE STATE, so an empty result can no longer be
    # the blindness check -- the DENOMINATOR is. A census that swept no models
    # or found no external commands has not measured anything, whatever its
    # finding count says.
    m = re.search(r"# models: (\d+)\s+external contexts: (\d+)\s+"
                  r"external commands: (\d+)", p.stderr)
    if not m:
        sys.exit("census printed no denominator -- refusing to trust its count")
    nmodels, nctx, ncmd = (int(x) for x in m.groups())
    if nmodels < 100 or nctx < 100 or ncmd < 100:
        sys.exit(f"census looks BLIND, not clean: {nmodels} models, {nctx} "
                 f"external contexts, {ncmd} external commands")
    print(f"swept {nmodels} models, {nctx} external contexts, "
          f"{ncmd} external commands")
    return {f"{r['model']}\t{r['ctx']}\t{r['id']}" for r in rows}


def main():
    now = current()
    if "--update" in sys.argv:
        BASELINE.write_text("\n".join(sorted(now)) + "\n")
        print(f"baseline refreshed: {len(now)} known gaps")
        return
    if not BASELINE.exists():
        sys.exit(f"no baseline at {BASELINE}; run with --update to create one")
    # an empty baseline file is legitimate: it means nothing is unsent
    known = {l for l in BASELINE.read_text().splitlines() if l.strip()}
    new = sorted(now - known)
    closed = sorted(known - now)
    print(f"unsent external commands: {len(now)} (baseline {len(known)})")
    if closed:
        print(f"{len(closed)} closed since the baseline -- refresh it with "
              f"--update so the ratchet tightens:")
        for c in closed[:20]:
            print("  - " + c.replace("\t", "  "))
        if len(closed) > 20:
            print(f"  ... and {len(closed) - 20} more")
    if new:
        print(f"\nFAIL: {len(new)} command(s) that nothing drives are NOT in "
              f"the baseline:")
        for c in new:
            print("  + " + c.replace("\t", "  "))
        print("\nEvery command an external context declares needs something to "
              "send it.\nSee BACKLOG #33 and scripts/adaptor-wiring/README.md; "
              "wire it, or add it\nto the baseline deliberately with a reason "
              "in BACKLOG.")
        sys.exit(1)
    print("OK: no new unsent commands")


main()
