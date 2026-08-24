#!/usr/bin/env python3
"""Enforce what a repository's ports may carry.

Reid, 2026-08-24, stated as a rule:

    REPOSITORIES CANNOT HAVE EVENT INLETS. They have command and query inlets
    and result outlets, and that's it. Some models might like to use a result
    outlet for command confirmations, but that's about it. Repositories don't
    generate events, they store data -- that IS the effect.

So: the effect of a command is a database update, the effect of a query is a
result response. An event never reaches a repository; a PROJECTOR turns an
entity event into the repository's own `Persist<E>` command.

riddlc does not check this directly -- it surfaces the consequence ("Inlet 'X'
admits Type 'E' but Repository 'R' declares no handler clause for N of its N
members") which reads as a missing-clause problem when the real defect is that
the inlet exists at all. This checks the rule itself.

**The type's DECLARED KIND is resolved, never inferred from its name.** A
name-based guess reports `LogStationEvent` as an event when it is declared
`command LogStationEvent`, and an alternation named `<X>Event` whose members are
commands would slip through the other way. Alternations are resolved to their
members.

Exit status is 1 if any violation is found, so this can gate a build.

Usage:  ./scripts/check-repository-ports.py [<model-dir> ...]
        (no arguments = whole corpus, patterns/ included)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = ("command", "query", "event", "result")


def block(s, i):
    j = s.index("{", i)
    d, k = 1, j + 1
    while d and k < len(s):
        d += (s[k] == "{") - (s[k] == "}")
        k += 1
    return s[i:k]


def declared_kinds(text):
    """name -> kind, for every message and alternation declared in the model."""
    kinds, alts = {}, {}
    for kind in KINDS:
        for m in re.finditer(rf"\b{kind}\s+(\w+)\s+(?:yields\s+\w+\s+\w+\s+)?is\b", text):
            kinds.setdefault(m.group(1), kind)
    for m in re.finditer(r"\btype\s+(\w+)\s+is\s+one\s+of\s*\{([^}]*)\}", text, re.S):
        # Split on the `or` separator; a bare token scan would take "or"
        # itself as a member, which resolves to nothing and poisons the result.
        alts[m.group(1)] = [x.strip().split(".")[-1]
                            for x in re.split(r"\bor\b", m.group(2)) if x.strip()]
    return kinds, alts


def resolve(name, kinds, alts, seen=None):
    """The set of declaration kinds a port type can admit."""
    seen = seen or set()
    if name in seen:
        return set()
    seen.add(name)
    if name in kinds:
        return {kinds[name]}
    if name in alts:
        out = set()
        for m in alts[name]:
            out |= resolve(m, kinds, alts, seen)
        return out or {"?"}
    return {"?"}


def main():
    args = sys.argv[1:]
    dirs = [ROOT / a for a in args] if args else sorted(
        {p.parent for p in ROOT.rglob("*.conf")})
    bad = 0
    for d in dirs:
        # ALWAYS recurse. reactive-bbq keeps its .riddl files in restaurant/,
        # corporate/ and backoffice/, so a non-recursive glob silently skips the
        # largest model in the corpus and reports a clean run.
        files = sorted(d.rglob("*.riddl"))
        if not files:
            continue
        text = "\n".join(p.read_text() for p in files)
        kinds, alts = declared_kinds(text)
        for p in files:
            s = p.read_text()
            for rm in re.finditer(r"repository\s+(\w+)\s+(?:as\s+\w+\s+)?is\s*\{", s):
                body = block(s, rm.start())
                for kind, port, typ in re.findall(
                        r"(inlet|outlet)\s+(\w+)\s+is\s+type\s+([\w.]+)", body):
                    got = resolve(typ.split(".")[-1], kinds, alts)
                    if kind == "inlet":
                        ok = got <= {"command", "query"}
                        want = "command or query"
                    else:
                        ok = got <= {"result"}
                        want = "result"
                    if not ok:
                        rel = p.relative_to(ROOT)
                        print(f"{rel}: repository {rm.group(1)} {kind} {port} "
                              f"is type {typ} -> {'/'.join(sorted(got))}, must be {want}")
                        bad += 1
    print(f"\n{bad} violation(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
