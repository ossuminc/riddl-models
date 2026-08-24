#!/usr/bin/env python3
"""Give an entity the `on event E` clause for each of its own events it is told.

BACKLOG #20, Reid 2026-08-22: *"handling the event is important to be able to
persist it."* An event nothing handles cannot be applied on replay, so the entity
that OWNS the event is the thing that must carry the clause. Both ruled tell
shapes converge here:

  shape 1  the entity's own command handler tells ITSELF the event
  shape 2  a split forwards the event AND tells the entity back

Either way the entity needs `on <e>: event E is { ... }`. This adds exactly that,
and nothing else -- the tell->yield conversion for shape 1 is a separate pass.

Driven by riddlc's own findings, never by guessing which events an entity has:

    Entity 'Ticket' is told Event 'EventCreated' but declares no handler clause
    that receives it, so the message cannot be delivered

The clause goes in a handler that is a DIRECT child of the entity, never one
nested inside a `state` -- a state's handler only applies while the entity is in
that state, so a replay clause there would silently not fire for events arriving
in any other state. An entity with no entity-level handler is reported and
skipped rather than guessed at.

Wording follows the corpus's own established phrasing for these clauses, which
`entertainment/live-events/ticket-sales` already carries for 6 of its 8 events.

Usage:  ./scripts/add-entity-event-clauses.py <model-dir> [...] [--dry-run]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
TOLD = re.compile(r"^Entity '(?P<ent>\w+)' is told Event '(?P<ev>\w+)' but declares no handler clause")


def entry_of(d):
    for c in sorted(d.glob("*.conf")):
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', c.read_text())
        if m:
            return m.group(1)
    return f"{d.name}.riddl"


def findings(d):
    r = subprocess.run([str(RIDDLC), "--no-ansi-messages", "validate", entry_of(d)],
                       cwd=d, capture_output=True, text=True)
    out, want = ANSI.sub("", r.stdout + "\n" + r.stderr), set()
    for ln in out.split("\n"):
        m = TOLD.match(ln.strip())
        if m:
            want.add((m.group("ent"), m.group("ev")))
    return want


def block(s, start):
    """(text, end_index) of the brace-balanced body opening at/after start."""
    i = s.index("{", start)
    d, j = 1, i + 1
    while d and j < len(s):
        d += (s[j] == "{") - (s[j] == "}")
        j += 1
    return s[start:j], j


def entity_handler(s, ent):
    """Span of a handler that is a DIRECT child of entity `ent`.

    Returns (insert_at, indent) or None. Handlers nested inside a `state` are
    skipped: such a handler is active only in that state, so a replay clause
    placed there would not fire for an event arriving in another one.
    """
    em = re.search(rf"^([ \t]*)(?:[\w-]+\s+)*entity\s+{ent}\s+(?:as\s+\w+\s+)?is\s*\{{", s, re.M)
    if not em:
        return None
    ebody, eend = block(s, em.start())
    base = em.start()
    # A handler may be declared `initial handler X is {`, so the keyword is
    # optional -- missing it made 438 entities look handler-less.
    for hm in re.finditer(r"^([ \t]*)(?:initial\s+)?handler\s+\w+\s+is\s*\{", ebody, re.M):
        # Reject if any `state ... is {` still open where this handler begins.
        prefix = ebody[:hm.start()]
        depth = 0
        for sm in re.finditer(r"^[ \t]*(?:initial\s+)?state\s+\w+\s+of\s+.*?\{", prefix, re.M):
            sb, send = block(ebody, sm.start())
            if send > hm.start():
                depth += 1
        if depth:
            continue
        _, hend = block(ebody, hm.start())
        close = ebody.rfind("}", 0, hend)
        return base + close, hm.group(1) + "  "
    return None


def main():
    dry = "--dry-run" in sys.argv
    added = skipped = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        want = findings(d)
        if not want:
            continue
        files = {p: p.read_text() for p in sorted(d.rglob("*.riddl"))}
        for ent, ev in sorted(want):
            binder = ev[0].lower() + ev[1:]
            target = None
            for p, s in files.items():
                if re.search(rf"^[ \t]*(?:[\w-]+\s+)*entity\s+{ent}\s+(?:as\s+\w+\s+)?is\s*\{{", s, re.M):
                    target = p
                    break
            if target is None:
                print(f"  SKIP {arg}: entity {ent} not found")
                skipped += 1
                continue
            s = files[target]
            if re.search(rf"^[ \t]*on \w+: event (?:[\w.]+\.)?{ev} is\b", s, re.M):
                continue  # already handled somewhere
            spot = entity_handler(s, ent)
            if spot is None:
                print(f"  SKIP {arg}: entity {ent} has no entity-level handler "
                      f"(only state handlers?) -- {ev} needs hand placement")
                skipped += 1
                continue
            at, ind = spot
            low = ent[0].lower() + ent[1:]
            clause = (f"{ind}on {binder}: event {ev} is {{\n"
                      f'{ind}  do "apply {ev} to the {low} so it can be persisted and replayed"\n'
                      f"{ind}}}\n")
            files[target] = s[:at] + clause + s[at:]
            added += 1
        if not dry:
            for p, s in files.items():
                p.write_text(s)
    print(f"\n{added} clauses {'would be ' if dry else ''}added, {skipped} skipped")


if __name__ == "__main__":
    main()
