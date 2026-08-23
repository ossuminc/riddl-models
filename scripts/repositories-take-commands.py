#!/usr/bin/env python3
"""Repositories take COMMANDS, not events (Reid, 2026-08-23).

A repository is not event-sourced: the effect of its commands is a change to
the database, and that is sufficient. So it must not declare inlets for events,
and nothing may send or tell it one. Turning an entity event into a repository
command is the PROJECTOR's job.

This applies that ruling:

  1. every EVENT inlet on a repository is removed, with the connector feeding
     it and -- if nothing else uses it -- the outlet and `send` statements at
     the far end
  2. the dead `<X>EventSource` / `<X>EventSink` / `<X>EventFlow` scaffolding is
     removed. A source has no inlet, so its handler can never fire; the sink
     existed only to tell events at the repository
  3. each projector gains an outlet of the repository's command type, a
     connector into a repository COMMAND inlet, and one `on event` clause per
     alternation member that sends the matching `Persist<Event>` command
  4. the repository gains those `Persist<Event>` commands, their `on command`
     clauses, and the command inlets

Ascriptions are deliberately NOT computed here -- arity changes throughout, and
riddlc derives the shape itself. Run scripts/collect-ascriptions.py and
scripts/apply-ascriptions.py afterwards.

The work list comes from riddlc, not from parsing: `collect-warnings.py` output
names every offending inlet and every missing alternation member. A model whose
shape this script cannot read confidently is HELD BACK and reported, never
guessed at -- same policy as rename-connectors.py.

STATUS 2026-08-23: NOT READY. Do not run this over the corpus yet.

The transformation is CORRECT and was proven by hand on
commerce/e-commerce/order-management: 48 findings -> 26, zero errors, with the
only remainder the entity-tell shape that BACKLOG #20 rules separately. This
script reproduces that shape but has two known defects:

  1. STALE OFFSETS. `find()` returns a match whose .start() is used again after
     the same file has been edited, so later insertions land at shifted
     positions. Symptom: `Path 'OrderRepositoryCommand' was not resolved` --
     the type IS emitted, into the wrong scope. Re-find after every edit, or
     collect all insertions per file and apply them back-to-front.
  2. `drop_block` OVER-CONSUMES. Removing an `<X>EventSource` swallows the
     `type <X>Event is one of {...}` declaration that follows it. Symptom:
     `Path 'ReturnEvent' was not resolved`. The `with { ... }` tail-swallowing
     is the likely culprit; bound it to a metadata block that starts on the
     same or next line.

Both are mechanical. Neither is a problem with the target shape.

Verify a fix the way the corpus was verified: run with --only on
commerce/e-commerce/order-management and require errors=0 and total=26.
Restore with `git checkout -- commerce/` between attempts.

Usage:
    ./scripts/collect-warnings.py > /tmp/w.jsonl
    ./scripts/repositories-take-commands.py /tmp/w.jsonl [--only MODEL] [--dry-run]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INLET_RE = re.compile(
    r"Inlet '(?P<inlet>\w+)' admits Type '(?P<type>[\w.]+)' but "
    r"(?P<kind>\w+) '(?P<owner>[\w.]+)' declares no handler clause for "
    r"(?P<miss>\d+) of its (?P<tot>\d+) members \((?P<members>[^)]*)\)"
)


def lower1(s):
    return s[0].lower() + s[1:]


class Model:
    """The .riddl files of one model, edited as text and written back once."""

    def __init__(self, model_dir):
        self.dir = ROOT / model_dir
        self.files = {p: p.read_text() for p in sorted(self.dir.glob("*.riddl"))}
        self.held = []

    def hold(self, why):
        self.held.append(why)

    # ---- lookup -------------------------------------------------------
    def find(self, pattern, flags=0):
        """(path, match) for the first file matching, else (None, None)."""
        for p, s in self.files.items():
            m = re.search(pattern, s, flags)
            if m:
                return p, m
        return None, None

    def alternation_members(self, name):
        """Members of `type <name> is one of { A or B }`, unqualified."""
        base = name.split(".")[-1]
        p, m = self.find(rf"\btype\s+{base}\s+is\s+one\s+of\s*\{{(.*?)\}}", re.S)
        if not m:
            return None
        return [x.split(".")[-1] for x in re.split(r"\s+or\s+", m.group(1).strip()) if x.strip()]

    def event_id_field(self, event):
        """(field, type) of an event's first field -- how a row is addressed."""
        base = event.split(".")[-1]
        for p, s in self.files.items():
            m = re.search(rf"\bevent\s+{base}\s+is\s*\{{", s)
            if not m:
                continue
            i = s.index("{", m.start())
            depth, j = 1, i + 1
            while depth and j < len(s):
                depth += (s[j] == "{") - (s[j] == "}")
                j += 1
            fm = re.search(r"^\s*(\w+)\s*:\s*([\w.]+(?:\([^)]*\))?)", s[i + 1:j - 1], re.M)
            if fm:
                return fm.group(1), fm.group(2)
        return None

    # ---- edits --------------------------------------------------------
    def drop_port(self, decl):
        """Remove a port declaration wherever prettify put it -- on its own
        line, or jammed onto a neighbour's."""
        pat = re.compile(r"[ \t]*" + re.escape(decl) + r"(?![\w])(\n)?")
        for p, s in self.files.items():
            new, n = pat.subn(lambda m: "" if m.group(1) is None else "\n", s, count=1)
            if n:
                self.files[p] = new
                return True
        return False

    def drop_block(self, header_re):
        """Remove a whole brace-balanced definition starting at header_re."""
        for p, s in self.files.items():
            m = re.search(header_re, s)
            if not m:
                continue
            i = s.index("{", m.start())
            depth, j = 1, i + 1
            while depth and j < len(s):
                depth += (s[j] == "{") - (s[j] == "}")
                j += 1
            # swallow a trailing `with { ... }` metadata block
            tail = re.match(r"\s*with\s*\{", s[j:])
            if tail:
                k = j + tail.end() - 1
                depth, j2 = 1, k + 1
                while depth and j2 < len(s):
                    depth += (s[j2] == "{") - (s[j2] == "}")
                    j2 += 1
                j = j2
            start = s.rfind("\n", 0, m.start()) + 1
            self.files[p] = s[:start] + s[j:].lstrip("\n")
            return True
        return False

    def drop_connector_to(self, inlet_suffix):
        """Remove connectors terminating on an inlet; return their outlets.

        Line-based on purpose. A regex with an optional `with { ... }` group
        under DOTALL over-consumes -- the lazy `.*?` still crosses lines
        hunting for a closing brace and will swallow whole definitions that
        follow. That deleted a `type` declaration on the first run.
        """
        outs = []
        head = re.compile(
            r"\s*connector\s+(?:'[^']*'|\w+)\s+is\s+from\s+outlet\s+([\w.]+)"
            r"\s+to\s+inlet\s+([\w.]+)")
        for p, s in list(self.files.items()):
            lines, out, i = s.split("\n"), [], 0
            while i < len(lines):
                m = head.match(lines[i])
                if m and m.group(2).endswith(inlet_suffix):
                    outs.append(m.group(1))
                    depth = lines[i].count("{") - lines[i].count("}")
                    i += 1
                    while depth > 0 and i < len(lines):
                        depth += lines[i].count("{") - lines[i].count("}")
                        i += 1
                    continue
                out.append(lines[i]); i += 1
            self.files[p] = "\n".join(out)
        return outs

    def write(self):
        for p, s in self.files.items():
            p.write_text(s)


def transform(model_dir, findings, dry_run=False):
    M = Model(model_dir)
    repo_inlets = [f for f in findings if f["kind"] == "Repository"]
    proj_inlets = [f for f in findings if f["kind"] == "Projector"]
    if not repo_inlets and not proj_inlets:
        return None

    repos = {f["owner"] for f in repo_inlets}
    if len(repos) > 1:
        M.hold(f"{len(repos)} repositories with event inlets; needs a per-repo decision")
        return M
    repo_path = next(iter(repos)) if repos else None
    repo = repo_path.split(".")[-1] if repo_path else None

    # ---- 1. strip the repository's event inlets and what feeds them ----
    for f in repo_inlets:
        M.drop_port(f"inlet {f['inlet']} is type {f['type']}")
        for outlet in M.drop_connector_to("." + f["inlet"]):
            short = outlet.split(".")[-1]
            M.drop_port(f"outlet {short} is type {f['type']}")
            for p, s in M.files.items():
                M.files[p] = re.sub(
                    rf"\n[ \t]*send \w+ to outlet (?:[\w.]+\.)?{short}(?![\w])", "", s)

    # ---- 2. remove the dead EventSource / EventSink / EventFlow trio ----
    for p, s in list(M.files.items()):
        for name in re.findall(r"processor (\w+EventSource) as ", s):
            M.drop_block(rf"[ \t]*processor {name} as \w+ is \{{")
        for name in re.findall(r"processor (\w+EventSink) as ", s):
            M.drop_block(rf"[ \t]*processor {name} as \w+ is \{{")
    for p, s in list(M.files.items()):
        M.files[p] = re.sub(
            r"[ \t]*connector\s+(?:'[^']*'|\w+)\s+is\s+from\s+outlet\s+[\w.]*"
            r"EventSource[\w.]*\s+to\s+inlet\s+[\w.]*EventSink[\w.]*"
            r"\s*(?:with\s*\{.*?\n[ \t]*\})?\n", "", M.files[p], flags=re.S)

    if not repo:
        return M

    # ---- 3. what each projector must now persist ----------------------
    persists = {}   # Event -> (idfield, idtype)
    plans = defaultdict(list)  # projector -> [(inlet, type, [members])]
    for f in proj_inlets:
        members = M.alternation_members(f["type"])
        if members is None:
            M.hold(f"cannot resolve alternation {f['type']}")
            return M
        missing = [m.strip() for m in f["members"].split(",") if m.strip()]
        for ev in missing:
            got = M.event_id_field(ev)
            if not got:
                M.hold(f"cannot find an identifying field on event {ev}")
                return M
            persists[ev] = got
        plans[f["owner"]].append((f["inlet"], f["type"], missing))

    if not persists:
        return M

    # ---- 4. repository gains the Persist commands and their clauses ----
    existing = set()
    for s in M.files.values():
        existing |= set(re.findall(r"command (Persist\w+) is", s))
    todo = [e for e in sorted(persists) if f"Persist{e}" not in existing]

    rp, rm = M.find(rf"[ \t]*repository {repo} as \w+ is \{{")
    if not rm:
        M.hold(f"cannot locate repository {repo}")
        return M

    decls = ""
    for ev in todo:
        fld, typ = persists[ev]
        decls += (
            f"    command Persist{ev} is  {{\n"
            f"      {fld}: {typ} with {{\n"
            f'        briefly "Row addressed"\n'
            f"        described as {{\n"
            f"          |Which stored row {ev} applies to.\n"
            f"        }}\n      }}\n    }} with {{\n"
            f'      briefly "Persist {ev}"\n'
            f"      described as {{\n"
            f"        |Instructs this repository to apply {ev} to the stored row. A\n"
            f"        |persistence command, not a domain command: it declares no `yields`\n"
            f"        |because storing a row records no new entity state.\n"
            f"      }}\n    }}\n")
    s = M.files[rp]
    at = s.index("{", rm.start()) + 1
    M.files[rp] = s[:at] + "\n" + decls + s[at:].lstrip("\n")

    # on-command clauses go in the repository's first handler
    hp, hm = M.find(rf"[ \t]*handler (\w+) is \{{")
    for p, s in M.files.items():
        m = re.search(r"[ \t]*handler (\w+) is \{", s[s.index(f"repository {repo} as"):]
                      if f"repository {repo} as" in s else "")
        if m:
            base = s.index(f"repository {repo} as")
            at = base + m.end()
            clauses = "".join(
                f"      on persist{ev}: command Persist{ev} is {{\n"
                f'        do "apply {ev} to the stored row"\n      }}\n'
                for ev in todo)
            M.files[p] = s[:at] + "\n" + clauses.rstrip("\n") + s[at:]
            break

    # the alternation the repository's command inlets admit
    alt = f"{repo}Command"
    all_persists = sorted(existing | {f"Persist{e}" for e in todo})
    if not M.find(rf"\btype\s+{alt}\s+is\s+one\s+of"):
        body = " or ".join(f"{repo_path}.{c}" for c in all_persists)
        decl = (f"  type {alt} is one of {{\n    {body}\n  }} with {{\n"
                f'    briefly "Anything that writes {repo}"\n'
                f"    described as {{\n"
                f"      |The persistence commands {repo} accepts. Entity events never reach\n"
                f"      |it directly; a projector turns each event into one of these first.\n"
                f"    }}\n  }}\n")
        s = M.files[rp]
        i = s.rfind("\n", 0, rm.start()) + 1
        M.files[rp] = s[:i] + decl + s[i:]

    # ---- 5. projector -> outlet -> connector -> repository command inlet
    conns = ""
    for proj_path, entries in plans.items():
        proj = proj_path.split(".")[-1]
        out = f"{proj}ToRepository"
        pp, pm = M.find(rf"[ \t]*projector {proj} as \w+ is \{{")
        if not pm:
            M.hold(f"cannot locate projector {proj}")
            return M
        s = M.files[pp]
        at = s.index("{", pm.start()) + 1
        M.files[pp] = s[:at] + f"\n    outlet {out} is type {alt}" + s[at:]

        inlet = f"{repo}From{proj}"
        s = M.files[rp]
        rm2 = re.search(rf"[ \t]*repository {repo} as \w+ is \{{", s)
        at = s.index("{", rm2.start()) + 1
        M.files[rp] = s[:at] + f"\n    inlet {inlet} is type {alt}" + s[at:]

        # one clause per missing member, sending the Persist command
        gen = ""
        for _, _, missing in entries:
            for ev in missing:
                fld, _ = persists[ev]
                b = lower1(ev)
                gen += (f"      on {b}: event {ev} is {{\n"
                        f"        send command {repo_path}.Persist{ev}("
                        f"{fld} = {b}.{fld}) to outlet {out}\n"
                        f'        do "apply {ev} to the {proj} projection"\n'
                        f"      }}\n")
        s = M.files[pp]
        base = s.index(f"projector {proj} as")
        hm2 = re.search(r"[ \t]*handler (\w+) is \{", s[base:])
        if not hm2:
            M.hold(f"projector {proj} has no handler to extend")
            return M
        at = base + hm2.end()
        M.files[pp] = s[:at] + "\n" + gen.rstrip("\n") + s[at:]

        conns += (f"  connector '{proj} Storage' is from outlet {proj_path}.{out}"
                  f" to inlet {repo_path}.{inlet} with {{\n"
                  f'    briefly "{proj} updates on their way to storage"\n  }}\n')

    if conns:
        s = M.files[rp]
        i = s.rindex("\n} with {") if "\n} with {" in s else s.rindex("\n}")
        M.files[rp] = s[:i + 1] + conns + s[i + 1:]

    return M


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    by_model = defaultdict(list)
    for line in open(argv[0]):
        r = json.loads(line)
        m = INLET_RE.search(r["message"])
        if m:
            d = m.groupdict()
            d["model"] = r["model"]
            by_model[r["model"]].append(d)

    done = held = 0
    for model, findings in sorted(by_model.items()):
        if only and only not in model:
            continue
        try:
            M = transform(model, findings, dry)
        except Exception as e:
            print(f"HELD  {model}: {type(e).__name__}: {e}")
            held += 1
            continue
        if M is None:
            continue
        if M.held:
            print(f"HELD  {model}: {M.held[0]}")
            held += 1
            continue
        if not dry:
            M.write()
        done += 1
    print(f"\ntransformed {done}, held back {held}")


if __name__ == "__main__":
    main()
