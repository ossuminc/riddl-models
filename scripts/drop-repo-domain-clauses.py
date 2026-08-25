#!/usr/bin/env python3
"""Remove DOMAIN command clauses from a repository's handler.

A repository is written through its OWN `Persist<Event>` commands (CLAUDE.md,
"A repository is written through its OWN Persist commands"). It must not handle
the entities' domain commands: `IssueLifePolicy` belongs to the LifePolicy
entity, and a repository clause for it duplicates the entity's, in a definition
that owns no state to change.

These duplicates are also what produce the "declares 'yields' but OnMessageClause
does not yield it on every path" errors. `yields` obliges EVERY handler of that
command, and the repository's copy answers with `tell event ... to entity`
instead of a `yield` -- which it cannot do, because only the owning entity may
yield its own event.

`scripts/repo-commands.py` phase 3 does this, but did not reach every model.

**A clause is removed only when some ENTITY in the same model already handles
that command.** If nothing else handles it, removing it would delete behaviour
rather than a duplicate, so the clause is kept and reported. `Persist*` commands
declared by the repository itself are never touched.

Usage:  ./scripts/drop-repo-domain-clauses.py <model-dir> [...] [--dry-run]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def body_of(s, start):
    """Text of the brace-balanced block opening at/after `start`."""
    j = s.index("{", start)
    d, k = 1, j + 1
    while d and k < len(s):
        d += (s[k] == "{") - (s[k] == "}")
        k += 1
    return s[start:k], k


def drop_clause(s, binder, cmd):
    """Remove one `on <binder>: command <cmd> is { ... }` clause, brace-balanced,
    INCLUDING any trailing `with { }` metadata block.

    An on-clause may carry its own `with { briefly ... described as ... }`. Taking
    only the brace-balanced body leaves that block orphaned, and the file then
    fails to parse at the stray `with {` -- which is how this first ran: the
    clauses in one model had no metadata and the ones in the next did.
    """
    head = f"{re.escape(binder)}: " if binder else ""
    m = re.search(rf"^[ \t]*on {head}command {re.escape(cmd)} is\s*\{{", s, re.M)
    if not m:
        return s, False
    _, end = body_of(s, m.start())
    t = re.match(r"[ \t\n]*with[ \t]*\{", s[end:])
    if t:
        _, end = body_of(s, end + t.end() - 1 - 1)
    while end < len(s) and s[end] in " \t":
        end += 1
    if end < len(s) and s[end] == "\n":
        end += 1
    return s[:m.start()] + s[end:], True


def main():
    dry = "--dry-run" in sys.argv
    total = kept = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        files = {p: p.read_text() for p in sorted(d.glob("*.riddl"))}
        # Every command any entity in this model handles.
        handled = set()
        for s in files.values():
            for em in re.finditer(r"\bentity\s+\w+\s+(?:as\s+\w+\s+)?is\s*\{", s):
                eb, _ = body_of(s, em.start())
                # A clause head may carry ANY number of qualifier segments
                # (`command LabContext.LabOrder.CollectSpecimen`); compare on the
                # last one, which is what the entity declares.
                handled |= {c.split(".")[-1]
                            for c in re.findall(r"on (?:\w+: )?command ([\w.]+) is", eb)}
        for p, s in list(files.items()):
            changed = False
            for rm in list(re.finditer(r"\brepository\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{", s)):
                rbody, _ = body_of(s, rm.start())
                own = set(re.findall(r"^\s*command\s+(\w+)\s", rbody, re.M))
                for binder, cmd in re.findall(r"on (?:(\w+): )?command ([\w.]+) is", rbody):
                    short = cmd.split(".")[-1]
                    if short in own or short.startswith("Persist"):
                        continue
                    if short not in handled:
                        print(f"  KEEP {arg}:{p.name} {rm.group(1)}.{cmd} "
                              f"- no entity handles it; removing would delete behaviour")
                        kept += 1
                        continue
                    s, ok = drop_clause(s, binder, cmd)
                    if ok:
                        print(f"  {'would drop' if dry else 'dropped'} "
                              f"{arg}:{p.name} {rm.group(1)}.{cmd}")
                        total += 1
                        changed = True
            if changed:
                files[p] = s
                if not dry:
                    p.write_text(s)
    print(f"\n{total} domain clauses {'would be ' if dry else ''}removed, {kept} kept")


if __name__ == "__main__":
    main()
