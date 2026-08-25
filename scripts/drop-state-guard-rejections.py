#!/usr/bin/env python3
"""Stop sending state-guard rejection events onto the wire.

Reid, 2026-08-24: *"nobody ever sends a message to a database telling it to
reject something... Whoever SENT those messages should not be sending them and
should be dealing with the rejection at THEIR level, not punting to the
database."*

The corpus emitted a `<Command>Rejected` event from every state-guard clause AND
raised an `error` in the same breath:

    on makeReservation: command MakeReservation is {
      send event MakeReservationRejected(reservationId = ..., rejectionReason =
        "Reservation does not accept MakeReservation in this state") to outlet ...
      error "Reservation does not accept MakeReservation in this state"
    }

The `error` is the handling. The event added nothing except a message on a
stream that eventually reached a repository, which is the punt.

**Only STATE GUARDS are removed, and the distinction is measured, not assumed.**
268 of the corpus's 269 rejection sends carry
`rejectionReason = "<X> does not accept <Y> in this state"` - a state-machine
guard. The one that does not is
`"Point balance is less than the points requested for redemption"`, which is a
genuine business rejection of the credit-card-declined kind Reid carved out, and
is LEFT ALONE. Anything whose reason is not the guard sentence is left alone.

Sites come from `riddlc dump --json` (send-statement nodes with their span), and
each statement is removed by span. The reason text is read from that span rather
than searched for.

Usage:  ./scripts/drop-state-guard-rejections.py <model-dir> [...] [--dry-run]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
GUARD = re.compile(r'rejectionReason = "\w+ does not accept \w+ in this state"')


def entry_of(d):
    for c in sorted(d.glob("*.conf")):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def dump(d, entry):
    r = subprocess.run([str(RIDDLC), "dump", entry, "--json"], cwd=d,
                       capture_output=True, text=True)
    out = ANSI.sub("", r.stdout)
    i = out.find("[")
    return json.loads(out[i:out.rfind("]") + 1]) if i >= 0 else []


def main():
    dry = "--dry-run" in sys.argv
    removed = kept = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        nodes = dump(d, entry_of(d))
        files, edits = {}, {}
        for n in nodes:
            if n.get("kind") != "send-statement":
                continue
            f = n["file"]
            if f not in files:
                files[f] = (d / f).read_text()
            sp = n["span"]
            a, b = sp["start"]["offset"], sp["end"]["offset"]
            text = files[f][a:b]
            if "Rejected(" not in text:
                continue
            if not GUARD.search(text):
                kept += 1
                print(f"  KEEP {arg}:{f}:{sp['start']['line']} "
                      f"not a state guard - a real business rejection")
                continue
            reason = GUARD.search(text).group(0).split(' = ', 1)[1]
            edits.setdefault(f, []).append((a, b, reason))
        for f, es in edits.items():
            s = files[f]
            for a, b, reason in sorted(es, key=lambda e: -e[0]):
                # take the whole line, including its indentation and newline
                ls = s.rfind("\n", 0, a) + 1
                indent = re.match(r"[ \t]*", s[ls:]).group(0)
                le = b
                while le < len(s) and s[le] != "\n":
                    le += 1
                rest = s[le + 1:]
                # Some guard clauses expressed the refusal ONLY as the event, so
                # removing it would leave an empty body -- illegal, and it would
                # also delete the refusal itself. Leave the `error` behind unless
                # the clause already raises one.
                nxt = rest.lstrip()
                head = s[:ls].rstrip().rsplit("\n", 1)[-1].strip()
                if nxt.startswith("}") and head.endswith("is {"):
                    s = s[:ls] + f"{indent}error {reason}\n" + rest
                else:
                    s = s[:ls] + rest
                removed += 1
            if not dry:
                (d / f).write_text(s)
        if edits:
            print(f"  {arg}: {sum(len(e) for e in edits.values())} guard send(s)")
    print(f"\n{removed} removed, {kept} kept as real rejections")


if __name__ == "__main__":
    main()
