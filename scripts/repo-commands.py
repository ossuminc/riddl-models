#!/usr/bin/env python3
"""Apply the mechanical half of "repositories take COMMANDS" to ONE model.

Reid, 2026-08-23: a repository is not event-sourced, so it declares no event
inlets and nothing may send it one. A PROJECTOR turns an entity event into a
repository command. Removing the inlets is necessary but insufficient -- the
sends feeding them are themselves the defect.

This does the parts that are identical everywhere. It does NOT finish a model:
every model has nuances, and the compiler is what drives the rest to zero. Run
it, then read `riddlc validate` and fix what is left BY HAND.

Proven recipe (order-management, 48 findings -> 0):

  mechanical, here          | by hand, after
  --------------------------|----------------------------------------------
  drop repo event inlets    | ascriptions riddlc names in its error text
  drop their connectors     | entity self-tell -> yield + `on event` clause
  drop split outlets/sends  | `yields` on the command, which then obliges
  drop EventSource/Sink/Flow|   EVERY handler -- relay `send` -> `forward`
  drop repo domain-command  | projector clauses: one per alternation member
    clauses                 |   `tell command R.Persist<E>(..) to repository R`
                            |   -- riddlc REJECTS `send` to an outlet here

Usage:  ./scripts/repo-commands.py <model-dir>
"""
import re
import sys
from pathlib import Path


def drop_port(s, decl):
    """Remove a port declaration wherever prettify put it -- on its own line or
    jammed onto a neighbour's."""
    pat = re.compile(r"[ \t]*" + re.escape(decl) + r"(?![\w])(\n)?")
    return pat.subn(lambda m: "" if m.group(1) is None else "\n", s, count=1)[0]


def drop_block(s, header_re):
    """Remove a brace-balanced definition, plus any trailing `with { }`.

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
    st = s.rfind("\n", 0, m.start()) + 1
    return s[:st] + s[j:].lstrip("\n"), True


def drop_connectors(s, pred):
    """Remove connectors whose (outlet, inlet) satisfies pred."""
    head = re.compile(r"\s*connector\s+(?:'[^']*'|\w+)\s+is\s+from\s+outlet\s+"
                      r"([\w.]+)\s+to\s+inlet\s+([\w.]+)")
    out, lines, i, hit = [], s.split("\n"), 0, []
    while i < len(lines):
        m = head.match(lines[i])
        if m and pred(m.group(1), m.group(2)):
            hit.append(m.group(1))
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
    d = Path(sys.argv[1])
    files = sorted(d.glob("*.riddl"))
    text = {p: p.read_text() for p in files}

    repos = set()
    for s in text.values():
        repos |= set(re.findall(r"\brepository\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{", s))

    # 1. every EVENT inlet on a repository, and what feeds it
    killed = []
    for p, s in text.items():
        for repo in repos:
            m = re.search(rf"\brepository\s+{repo}\s+(?:as\s+\w+\s+)?is\s*\{{", s)
            if not m:
                continue
            i = s.index("{", m.start())
            depth, j = 1, i + 1
            while depth and j < len(s):
                depth += (s[j] == "{") - (s[j] == "}")
                j += 1
            for iname, ityp in re.findall(r"inlet (\w+) is type ([\w.]+)", s[i:j]):
                if re.search(rf"\btype\s+{ityp.split('.')[-1]}\s+is\s+one\s+of",
                             "\n".join(text.values()), re.S) and "Command" not in ityp:
                    killed.append((iname, ityp))
            text[p] = s
    for iname, ityp in killed:
        for p in list(text):
            text[p] = drop_port(text[p], f"inlet {iname} is type {ityp}")
        for p in list(text):
            text[p], outs = drop_connectors(text[p], lambda o, i, n=iname: i.endswith("." + n))
            for o in outs:
                short = o.split(".")[-1]
                for q in list(text):
                    text[q] = drop_port(text[q], f"outlet {short} is type {ityp}")
                    text[q] = re.sub(
                        rf"\n[ \t]*send \w+ to outlet (?:[\w.]+\.)?{short}(?![\w])", "", text[q])

    # 2. the dead EventSource / EventSink / EventFlow scaffolding
    for p in list(text):
        for kind in ("EventSource", "EventSink"):
            while True:
                names = re.findall(rf"processor (\w+{kind}) as ", text[p])
                if not names:
                    break
                text[p], ok = drop_block(text[p], rf"[ \t]*processor {names[0]} as \w+ is \{{")
                if not ok:
                    break
        text[p], _ = drop_connectors(
            text[p], lambda o, i: "EventSource" in o and "EventSink" in i)

    # 3. a repository must not handle the entities' DOMAIN commands
    ents = set()
    for s in text.values():
        ents |= set(re.findall(r"\bentity\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{", s))
    for p in list(text):
        s = text[p]
        for repo in repos:
            m = re.search(rf"\brepository\s+{repo}\s+(?:as\s+\w+\s+)?is\s*\{{", s)
            if not m:
                continue
            i = s.index("{", m.start())
            depth, j = 1, i + 1
            while depth and j < len(s):
                depth += (s[j] == "{") - (s[j] == "}")
                j += 1
            blk = s[i:j]
            for e in ents:
                blk = re.sub(
                    rf"[ \t]*on \w+: command {e}\.\w+ is \{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}}\n", "", blk)
                blk = re.sub(
                    rf"[ \t]*on command {e}\.\w+ is \{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}}\n", "", blk)
            s = s[:i] + blk + s[j:]
        text[p] = s

    for p, s in text.items():
        p.write_text(s)
    print(f"{d}: dropped {len(killed)} event inlets")


if __name__ == "__main__":
    main()
