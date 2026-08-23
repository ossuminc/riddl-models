#!/usr/bin/env python3
"""Wire a repository so its OWN `Persist` commands can actually reach it.

The "repositories take COMMANDS" ruling (BACKLOG #20) removes a repository's
event inlets. Removing them is necessary but INSUFFICIENT: with no inlets the
repository is unreachable, and every `tell ... to repository R` in a projector
becomes a warning. This adds the four things that make it real, exactly as the
proven reference `commerce/e-commerce/order-management` has them:

  1. `type <R>Command is one of { <all its Persist commands> }` at context scope
  2. `inlet <R>From<P> is type <R>Command`  in the repository
  3. `outlet <P>ToRepository is type <R>Command`  in the projector
  4. `connector '<P> Storage'` joining 3 -> 2

The projector keeps using `tell command R.Persist<E>(..) to repository R` --
that is the reference's form, and the connector exists to make the tell
DELIVERABLE, not to carry a `send`. (BACKLOG #20's code block showing
`send ... to outlet` predates the reference and disagrees with it; the model on
disk is the authority.)

Ascriptions are NOT touched here -- adding ports changes arity, so run
`scripts/reascribe.py <model-dir>` afterwards and let riddlc name each shape.

Every insertion is anchored on text that must be present exactly once; a model
that does not match is reported and left ALONE rather than guessed at.

Usage:  ./scripts/wire-repo-commands.py <model-dir> [...] [--dry-run]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def block_end(s, start):
    """Index just past the brace-balanced body opening at/after `start`."""
    i = s.index("{", start)
    depth, j = 1, i + 1
    while depth and j < len(s):
        depth += (s[j] == "{") - (s[j] == "}")
        j += 1
    return j


def wire_file(path, dry):
    s = orig = path.read_text()
    # A context may carry its own `as <shape>` ascription between name and `is`.
    ctx = re.search(r"^\s*(?:\w+\s+)*context\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{", s, re.M)
    if not ctx:
        return 0, []
    C, notes, changes = ctx.group(1), [], 0

    for rm in list(re.finditer(r"^(\s*)repository\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{", s, re.M)):
        R, ind = rm.group(2), rm.group(1)
        body = s[rm.start():block_end(s, rm.start())]
        persists = sorted(set(re.findall(r"^\s*command\s+(Persist\w+)\s", body, re.M)))
        if not persists:
            notes.append(f"{R}: no Persist commands, skipped")
            continue
        if re.search(rf"^\s*inlet\s+\w+\s+is\s+type\s+{R}Command\b", body, re.M):
            notes.append(f"{R}: already wired, skipped")
            continue

        # Which projectors update this repository AND tell its Persist commands?
        projs = []
        for pm in re.finditer(r"^(\s*)projector\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{", s, re.M):
            P = pm.group(2)
            pbody = s[pm.start():block_end(s, pm.start())]
            if re.search(rf"updates\s+repository\s+[\w.]*\b{R}\b", pbody) and \
               re.search(rf"\b{R}\.Persist\w+", pbody):
                projs.append((P, pm.start()))
        if not projs:
            notes.append(f"{R}: no projector both updates it and tells its Persist commands, skipped")
            continue
        # Several projectors may feed one repository. Each gets its OWN outlet,
        # its OWN inlet on the repository, and its OWN connector -- which is why
        # the naming convention names these legs for the PROJECTOR, not the type
        # (CLAUDE.md, Connector Naming): the type alone cannot tell them apart.
        pnames = [p for p, _ in projs]

        # 1. the alternation, immediately before the repository
        alt = " or ".join(f"{C}.{R}.{c}" for c in persists)
        decl = (f"{ind}type {R}Command is one of {{\n"
                f"{ind}  {alt}\n"
                f"{ind}}} with {{\n"
                f'{ind}  briefly "Anything that writes the {R}"\n'
                f"{ind}  described as {{\n"
                f"{ind}    |The persistence commands {R} accepts. Entity events never\n"
                f"{ind}    |reach it directly; the projector turns each event into one of these.\n"
                f"{ind}  }}\n"
                f"{ind}}}\n")
        if f"type {R}Command is one of" not in s:
            s = s[:rm.start()] + decl + s[rm.start():]

        failed = False
        for P in pnames:
            # 2. this projector's command inlet on the repository -- before the
            #    first outlet if there is one, else at the top of the body.
            rm2 = re.search(rf"^(\s*)repository\s+{R}\s+(?:as\s+\w+\s+)?is\s*\{{", s, re.M)
            rbody_end = block_end(s, rm2.start())
            om = re.search(r"^(\s*)outlet\s+\w+\s+is\s+type\s+.*$", s[rm2.start():rbody_end], re.M)
            if om:
                at = rm2.start() + om.start()
                s = s[:at] + f"{om.group(1)}inlet {R}From{P} is type {R}Command\n" + s[at:]
            else:
                at = s.index("\n", rm2.start()) + 1
                s = s[:at] + f"{ind}  inlet {R}From{P} is type {R}Command\n" + s[at:]

            # 3. the projector's outlet -- after its first inlet
            pm2 = re.search(rf"^(\s*)projector\s+{P}\s+(?:as\s+\w+\s+)?is\s*\{{", s, re.M)
            pend = block_end(s, pm2.start())
            im = re.search(r"^(\s*)inlet\s+\w+\s+is\s+type\s+.*$", s[pm2.start():pend], re.M)
            if not im:
                notes.append(f"{R}: projector {P} has no inlet to anchor on, model left alone")
                failed = True
                break
            at = pm2.start() + im.end()
            s = s[:at] + f"\n{im.group(1)}outlet {P}ToRepository is type {R}Command" + s[at:]

            # 4. the connector, beside the existing ones
            conn = (f"{ind}connector '{P} Storage' is from outlet {C}.{P}.{P}ToRepository "
                    f"to inlet {C}.{R}.{R}From{P} with {{\n"
                    f'{ind}  briefly "{P} projections on their way to storage"\n'
                    f"{ind}}}\n")
            cm = re.search(rf"^{ind}connector\s+", s, re.M)
            if not cm:
                notes.append(f"{R}: no connector block to anchor on, model left alone")
                failed = True
                break
            s = s[:cm.start()] + conn + s[cm.start():]

        if failed:
            s = orig
            continue
        changes += 1
        notes.append(f"{R}: wired via {', '.join(pnames)} ({len(persists)} Persist commands)")

    if changes and not dry:
        path.write_text(s)
    return changes, notes


def main():
    dry = "--dry-run" in sys.argv
    total = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        for p in sorted(d.glob("*.riddl")):
            n, notes = wire_file(p, dry)
            total += n
            for note in notes:
                print(f"  {arg}/{p.name}: {note}")
    print(f"\n{total} repositories {'would be ' if dry else ''}wired")


if __name__ == "__main__":
    main()
