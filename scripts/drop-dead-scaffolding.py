#!/usr/bin/env python3
"""Delete the `<X>Source` / `<X>Sink` streamlets the ruling calls dead.

Reid, 2026-08-23 (BACKLOG #20.4): `<X>EventSource` / `<X>EventSink` /
`<X>EventFlow` are dead scaffolding and are to be deleted -- "a wasteful lot of
extra duplicate processing". No source has an inlet, so its handler can never
fire; the sinks existed only to `tell` entity EVENTS at a repository, which is
exactly what "repositories take COMMANDS" forbids.

`scripts/repo-commands.py` already does this, but matches only the literal
`\\w+EventSource` / `\\w+EventSink`. Much of the corpus names them `<X>Source` /
`<X>Sink` with no `Event` infix, and those were silently left behind -- carrying
`on init` clauses that name `Initialize<X>` commands deleted earlier in the
campaign, which is where 46 of the remaining errors come from (23 unresolved
paths, each with a paired "does not name a message value").

The end state is proven: `commerce/e-commerce/order-management` and
`.../product-catalog` are both at ZERO findings of every severity and retain no
source or sink at all -- only their `<X>EventSplit as flow`.

**Matched by NAME SUFFIX and SHAPE together**, deliberately narrowly:
a processor ascribed `as source` whose name ends in `Source`, or ascribed
`as sink` whose name ends in `Sink`. reactive-bbq's `<X>EventLog as sink`
streamlets do NOT end in `Sink` and are left alone -- that model is a separate
reference at zero errors and its event logs are not this scaffolding.

Anything still REFERRING to a deleted processor after the fact is reported. A
model with dangling references is restored untouched rather than left broken.

Usage:  ./scripts/drop-dead-scaffolding.py <model-dir> [...] [--dry-run]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def drop_block(s, header_re):
    """Remove a brace-balanced definition plus any trailing `with { }`.

    Line/brace counting, never a DOTALL regex: an optional `with {...}` group
    under DOTALL has a lazy `.*?` that still crosses lines hunting a closing
    brace, and it will swallow whole definitions that follow.
    """
    m = re.search(header_re, s)
    if not m:
        return s, False
    i = s.index("{", m.start())
    depth, j = 1, i + 1
    while depth and j < len(s):
        depth += (s[j] == "{") - (s[j] == "}")
        j += 1
    t = re.match(r"[ \t]*with[ \t]*\{", s[j:])
    if t:
        k = j + t.end() - 1
        depth, j2 = 1, k + 1
        while depth and j2 < len(s):
            depth += (s[j2] == "{") - (s[j2] == "}")
            j2 += 1
        j = j2
    while j < len(s) and s[j] in " \t":
        j += 1
    if j < len(s) and s[j] == "\n":
        j += 1
    start = m.start()
    while start > 0 and s[start - 1] in " \t":
        start -= 1
    return s[:start] + s[j:], True


def drop_connectors(s, names):
    """Remove connectors whose outlet or inlet path names a deleted processor."""
    head = re.compile(r"\s*connector\s+(?:'[^']*'|\w+)\s+is\s+from\s+outlet\s+"
                      r"([\w.]+)\s+to\s+inlet\s+([\w.]+)")
    out, lines, i, hit = [], s.split("\n"), 0, 0
    while i < len(lines):
        m = head.match(lines[i])
        if m and any(f".{n}." in f".{m.group(1)}." or f".{n}." in f".{m.group(2)}."
                     for n in names):
            hit += 1
            d = lines[i].count("{") - lines[i].count("}")
            i += 1
            while d > 0 and i < len(lines):
                d += lines[i].count("{") - lines[i].count("}")
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), hit


def main():
    dry = "--dry-run" in sys.argv
    tot_p = tot_c = 0
    for arg in [a for a in sys.argv[1:] if a != "--dry-run"]:
        d = (ROOT / arg).resolve()
        orig = {p: p.read_text() for p in sorted(d.glob("*.riddl"))}
        text = dict(orig)
        killed = []
        for p in list(text):
            for suffix, shape in (("Source", "source"), ("Sink", "sink")):
                while True:
                    names = re.findall(rf"processor\s+(\w*{suffix})\s+as\s+{shape}\s+is\s*\{{",
                                       text[p])
                    if not names:
                        break
                    text[p], ok = drop_block(
                        text[p], rf"[ \t]*processor\s+{names[0]}\s+as\s+{shape}\s+is\s*\{{")
                    if not ok:
                        break
                    killed.append(names[0])
        if not killed:
            continue
        ncon = 0
        for p in list(text):
            text[p], n = drop_connectors(text[p], killed)
            ncon += n

        # Refuse to leave a model with a dangling reference to something deleted.
        dangling = []
        for p, s in text.items():
            for n in killed:
                for m in re.finditer(rf"\b{n}\b", s):
                    dangling.append(f"{p.name}: {s[:m.start()].count(chr(10))+1}: {n}")
        if dangling:
            print(f"  {arg}: RESTORED - {len(dangling)} dangling refs after deleting "
                  f"{', '.join(killed)}")
            for x in dangling[:4]:
                print(f"      {x}")
            continue

        print(f"  {arg}: dropped {len(killed)} ({', '.join(killed)}) + {ncon} connectors")
        tot_p += len(killed)
        tot_c += ncon
        if not dry:
            for p, s in text.items():
                p.write_text(s)
    print(f"\n{tot_p} processors, {tot_c} connectors {'would be ' if dry else ''}dropped")


if __name__ == "__main__":
    main()
