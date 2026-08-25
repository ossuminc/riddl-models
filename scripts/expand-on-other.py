#!/usr/bin/env python3
"""Replace a blanket `on other` with an explicit clause per union member.

`on other` is legal and sometimes right, but it is the weak answer when the
members it swallows are real lifecycle events rather than a genuinely uniform
"nothing happens" case. In reactive-bbq it was hiding `VisitCompleted`,
`TicketRouted`, `DrinkOrderReceived`, `StationAssigned` and `ShiftCreated` -
events the model plainly cares about - alongside the `<Command>Rejected` ones.

**The behaviour is derived from the processor itself, never invented.** Each of
these processors already handles SOME members of its inlet's union. If those
existing clauses are UNIFORM in shape - all forwarding to the same outlet, or all
telling the same command with the same argument shape - that shape is the
processor's policy, and it is applied to the uncovered members with their own
binder substituted. Where the existing clauses disagree with each other, the
processor has no single policy to copy, so the site is reported and left for a
human rather than guessed at.

Structure comes from `riddlc dump --json`: inlets, their unions already resolved
to members, each handler's clauses and spans. No RIDDL is parsed here beyond
reading the spans the projection hands over.

Usage:  ./scripts/expand-on-other.py <model-dir> [--dry-run] [--list]
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLC = ROOT.parent / "bin" / "riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
MARKS = ("remaining members of this inlet", "not persisted:")


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


def low(s):
    return s[0].lower() + s[1:]


def body_of(text):
    """The statements inside a clause's braces, normalised to one per line."""
    i = text.index("{")
    d, j = 1, i + 1
    while d and j < len(text):
        d += (text[j] == "{") - (text[j] == "}")
        j += 1
    return [l.strip() for l in text[i + 1:j - 1].strip().split("\n") if l.strip()]


def template(clauses, binders, events):
    """A single statement-shape shared by every clause, parameterised.

    BOTH the binder and the event's own name are blanked, because a policy like
    "tell Persist<ThisEvent>" or a prompt naming the event is one policy
    expressed per member -- comparing the raw text would call those clauses
    different and hold back every projector in the corpus.

    Returns the lines with the binder as {b} and the event name as {E}/{e}, or
    None if the clauses still disagree, meaning there is no single policy.
    """
    shapes = []
    for txt, b, ev in zip(clauses, binders, events):
        lines = body_of(txt)
        out = []
        for l in lines:
            # No lookbehind on the event name: it appears as a SUFFIX in
            # `PersistCustomerEnrolled`, which is exactly the varying part.
            l = re.sub(rf"{re.escape(ev)}(?![\w])", "{E}", l)
            l = re.sub(rf"(?<![\w]){re.escape(low(ev))}(?![\w])", "{e}", l)
            l = re.sub(rf"(?<![\w]){re.escape(b)}(?![\w])", "{b}", l)
            out.append(l)
        shapes.append(tuple(out))
    return list(shapes[0]) if len(set(shapes)) == 1 else None


def main():
    dry = "--dry-run" in sys.argv or "--list" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = (ROOT / args[0]).resolve()
    entry = entry_of(d)
    nodes = dump(d, entry)
    bp, bypath = defaultdict(list), {}
    for n in nodes:
        bp[n.get("parent")].append(n)
        if n.get("path"):
            bypath[n["path"]] = n
    files = {}

    def src(n):
        f = n["file"]
        if f not in files:
            files[f] = (d / f).read_text()
        s = n["span"]
        return files[f][s["start"]["offset"]:s["end"]["offset"]]

    edits, held = defaultdict(list), 0
    for o in [n for n in nodes if n.get("kind") == "on-other"]:
        try:
            otext = src(o)
        except Exception:
            continue
        if not any(m in otext for m in MARKS):
            continue
        h = bypath.get(o["parent"])
        proc = bypath.get(h["parent"]) if h else None
        if not proc:
            continue
        # An event clause is kind `on-event`; `onmessageclause` covers commands
        # and queries. Looking at only one of them reports every handler as
        # having zero clauses.
        clauses = [c for c in bp[h["path"]]
                   if c.get("kind") in ("on-event", "onmessageclause")]
        texts, binders, evnames, handled = [], [], [], set()
        for c in clauses:
            t = src(c)
            m = re.match(r"on (\w+): (?:event|command) ([\w.]+) is", t)
            if not m:
                continue
            texts.append(t)
            binders.append(m.group(1))
            evnames.append(m.group(2).split(".")[-1])
            handled.add(m.group(2).split(".")[-1])
        tpl = template(texts, binders, evnames) if texts else None
        uncovered = []
        for i in [k for k in bp[proc["path"]] if k.get("kind") == "inlet"]:
            for mem in (i.get("type") or {}).get("alternation", []):
                if mem["ref"].split(".")[-1] not in handled:
                    uncovered.append(mem["ref"])
        if not uncovered:
            continue
        if tpl is None:
            print(f"  HOLD {proc['kind']} {proc['id']}: its {len(texts)} existing clauses "
                  f"disagree, so there is no single policy to extend to "
                  f"{len(uncovered)} member(s)")
            held += 1
            continue
        ind = re.match(r"[ \t]*", otext).group(0) or "      "
        new = ""
        for ref in uncovered:
            E = ref.split(".")[-1]
            b = low(E)
            new += (f"{ind}on {b}: event {ref} is {{\n"
                    + "".join(f"{ind}  " + l.replace("{E}", E).replace("{e}", low(E))
                              .replace("{b}", b) + "\n" for l in tpl)
                    + f"{ind}}}\n")
        edits[o["file"]].append((o["span"]["start"]["offset"],
                                 o["span"]["end"]["offset"], new, proc, len(uncovered)))
        print(f"  {proc['kind']} {proc['id']}: on other -> {len(uncovered)} explicit clause(s)")

    total = 0
    for f, es in edits.items():
        s = files[f]
        for a, b, new, _, n in sorted(es, key=lambda e: -e[0]):
            # swallow the trailing newline of the replaced clause, if any
            end = b + 1 if b < len(s) and s[b] == "\n" else b
            s = s[:a] + new.lstrip() + s[end:]
            total += n
        if not dry:
            (d / f).write_text(s)
    print(f"\n{total} clause(s) {'would be ' if dry else ''}written, {held} processor(s) held")


if __name__ == "__main__":
    main()
