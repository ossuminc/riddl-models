#!/usr/bin/env python3
"""Rename Link<Source>To<Target> connectors for what flows through them.

The old convention restated the endpoints the declaration already gives --
`from outlet X to inlet Y` says source, target and direction, so
`LinkSalesReportToSalesReportRepository` adds nothing but length. Worse, each
connector's `briefly` was the name again, so the one place that could have said
what the pipe carries said nothing at all.

The corpus wires every entity the same way: entity -> EventSplit -> {repository,
projector}, with an application on either side for commands and query results.
That gives five roles, and a name is <Subject><Role>:

    <E>EventStream     the entity's events, fanned out
    <E>EventStorage    those events on their way to storage
    <P>Feed            events feeding a projection
    <P>Storage         a projection on its way to storage
    <E>CommandStream   commands from the application
    <E>QueryResults    results going back to the application

The role words avoid `Commands` and `Persistence`, which read better but are
already taken: an entity's command inlet is `<E>Commands` (737 of them) and a
repository's handler is `<E>Persistence` (489). Reusing either makes the
connector overload an existing definition, which riddlc reports as a warning.
Verified by counting every declared identifier per model before choosing.

usage: rename-connectors.py [<dir> ...] [--apply]
"""
import re, sys, glob, os, collections

RULES = [
    (r'LinkApp(\w+)RepositoryResponses', lambda m: (m.group(1) + "QueryResults",
        f"{m.group(1)} query results returned to the application")),
    (r'LinkApp(\w+)Commands', lambda m: (m.group(1) + "CommandStream",
        f"{m.group(1)} commands from the application")),
    (r'Link(\w+)To(\w+)EventSplit', lambda m: (m.group(1) + "EventStream",
        f"{m.group(1)} events, fanned out to storage and read models")),
    (r'Link(\w+)EventSplitTo(\w+)Repository', lambda m: (m.group(1) + "EventStorage",
        f"{m.group(1)} events on their way to storage")),
    (r'Link(\w+)EventSplitTo(\w+)', lambda m: (m.group(2) + "Feed",
        f"{m.group(1)} events feeding the {m.group(2)} projection")),
    (r'Link(\w+)To\1Repository', lambda m: (m.group(1) + "EventStorage",
        f"{m.group(1)} events on their way to storage")),
    (r'Link(\w+)To(\w+)Repository', lambda m: (m.group(1) + "Storage",
        f"The {m.group(1)} projection on its way to storage")),
]


def rename(name):
    for pat, fn in RULES:
        m = re.fullmatch(pat, name)
        if m:
            return fn(m)
    return None


def plan(files):
    """Map old -> (new, briefly), and report names that clash inside one file."""
    mapping, clashes = {}, []
    for f in files:
        text = open(f).read()
        names = [m.group(1) for m in re.finditer(r'connector (\w+) is from', text)]
        proposed = collections.defaultdict(list)
        for n in names:
            if not n.startswith("Link"):
                continue
            r = rename(n)
            if r is None:
                clashes.append((f, n, "no rule"))
                continue
            proposed[r[0]].append(n)
            mapping[(f, n)] = r
        for new, olds in proposed.items():
            if len(olds) > 1:
                clashes.append((f, new, olds))
                for o in olds:
                    mapping.pop((f, o), None)   # hold back; needs a human decision
    return mapping, clashes


def main(argv):
    apply_ = "--apply" in argv
    roots = [a for a in argv[1:] if not a.startswith("--")] or ["."]
    files = sorted(set(sum(
        [glob.glob(os.path.join(r, "**", "*.riddl"), recursive=True) for r in roots], [])))
    mapping, clashes = plan(files)

    per_file = collections.defaultdict(dict)
    for (f, old), val in mapping.items():
        per_file[f][old] = val

    for f, m in sorted(per_file.items()):
        text = open(f).read()
        for old, (new, brief) in m.items():
            text = re.sub(rf'\bconnector {old} is from\b', f'connector {new} is from', text)
            text = text.replace(f'briefly "{old}"', f'briefly "{brief}"')
        if apply_:
            open(f, 'w').write(text)
    print(f"{'APPLIED' if apply_ else 'DRY RUN'}: {len(mapping)} connectors renamed "
          f"in {len(per_file)} files")
    if clashes:
        print(f"HELD BACK ({len(clashes)}) -- these need a naming decision:")
        for f, new, olds in clashes:
            print(f"  {f}: {new} <- {olds}")


main(sys.argv)
