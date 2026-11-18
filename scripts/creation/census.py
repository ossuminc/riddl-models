#!/usr/bin/env python3
"""Census of how each stateful entity is created, for the on-init migration.

riddl 2.8.0's creation model: a context `create`s the entity and the entity's
own entity-level `on init(args)` morphs it into its starting state. The corpus
still has the older shape, which riddlc 2.7.0-20 reports as
`entity-init-in-state` / `entity-init-no-morph`:

    state S0 { on init { let e: type E = prompt(...); yield e } }   # bridge
    on e: event E { morph entity X to state S0 with record R(...) }  # fold
    on c: command C { yield event E(...) }                           # creator
    (in the context)  on c: command X.C { forward c to outlet ... }  # relay

For every entity with states this reports, from `riddlc dump --json` alone:
the starting state S0 (the first declared), the creation event E its on init
yields, E's fold and whether it morphs into S0, the entity clauses that yield
E, and the clauses outside the entity that handle the creating command.

Usage:  ./scripts/creation/census.py [model-dir ...]   (default: all models)
Writes TSV to stdout, one row per entity.
"""
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()


def models():
    for conf in sorted(ROOT.rglob("*.conf")):
        rel = conf.parent.relative_to(ROOT)
        if rel.parts and rel.parts[0] in ("patterns", "project", "target", "scripts"):
            continue
        if (conf.parent / (conf.stem + ".riddl")).exists() and conf.stem == conf.parent.name:
            yield conf.parent


def dump(mdir):
    out = subprocess.run([str(RIDDLC), "dump", mdir.name + ".riddl", "--json"],
                         cwd=mdir, capture_output=True, text=True)
    if not out.stdout.strip():
        raise SystemExit(f"dump failed: {mdir}\n{out.stderr[-400:]}")
    return json.loads(out.stdout)


def under(path, prefix):
    return path == prefix or path.startswith(prefix + ".")


def census(mdir):
    nodes = dump(mdir)
    by_parent = defaultdict(list)
    for n in nodes:
        by_parent[n.get("parent", "")].append(n)
    rows = []
    for ent in [n for n in nodes if n["kind"] == "entity"]:
        ep = ent["path"]
        states = sorted([n for n in nodes if n["kind"] == "state"
                         and n["parent"] == ep],
                        key=lambda s: (s["file"], s["span"]["start"]["offset"]))
        if not states:
            continue
        s0 = states[0]
        inits = [n for n in nodes if n["kind"] == "on-init" and under(n["parent"], ep)]
        state_inits = [i for i in inits if any(under(i["parent"], s["path"]) for s in states)]
        entity_inits = [i for i in inits if i not in state_inits]
        s0_init = [i for i in state_inits if under(i["parent"], s0["path"])]
        event = ""
        if s0_init:
            lets = [n for n in by_parent[s0_init[0]["path"]] if n["kind"] == "let-statement"]
            if lets and lets[0].get("declaredType"):
                event = lets[0]["declaredType"].get("resolved", "")
        folds = [n for n in nodes if n["kind"] == "on-event" and under(n["parent"], ep)
                 and n.get("message", {}).get("resolved") == event] if event else []
        fold_morph = ""
        if len(folds) == 1:
            ms = [n for n in by_parent[folds[0]["path"]] if n["kind"] == "morph-statement"]
            fold_morph = ("S0" if ms and ms[0]["state"].get("resolved") == s0["path"]
                          else (ms[0]["state"].get("resolved", "?").rsplit(".", 1)[-1] if ms else "none"))
        creators = []
        if event:
            for n in nodes:
                if n["kind"] == "yield-statement" and n.get("message", {}).get("resolved") == event \
                        and under(n["parent"], ep) and " " in n["parent"].rsplit(".", 1)[-1] \
                        and n["parent"].rsplit(".", 1)[-1].startswith("command "):
                    creators.append(n["parent"])
        creators = sorted(set(creators))
        cmd_paths = []
        for c in creators:
            clause = next((n for n in nodes if n.get("path") == c), None)
            if clause:
                cmd_paths.append(clause.get("message", {}).get("resolved", ""))
        relays = []
        for cp in cmd_paths:
            for n in nodes:
                if n["kind"] == "onmessageclause" and n.get("message", {}).get("resolved") == cp \
                        and not under(n["parent"], ep):
                    kinds = sorted({s["kind"].replace("-statement", "")
                                    for s in by_parent[n["path"]]
                                    if s["kind"].endswith("-statement")})
                    relays.append(n["parent"].rsplit(".", 1)[-1] + ":" + "+".join(kinds))
        rows.append([
            str(mdir.relative_to(ROOT)), ent["id"],
            "+".join(ent.get("intentions", [])) or "-",
            str(len(states)), s0["id"],
            str(len(state_inits)), str(len(entity_inits)),
            event.rsplit(".", 1)[-1] or "-",
            str(len(folds)), fold_morph or "-",
            str(len(creators)),
            ",".join(c.rsplit(".", 1)[-1] for c in cmd_paths) or "-",
            ";".join(relays) or "-",
        ])
    return rows


def main():
    dirs = [ROOT / a for a in sys.argv[1:]] or list(models())
    print("\t".join(["model", "entity", "intentions", "states", "s0",
                     "stateInits", "entityInits", "event", "folds", "foldMorph",
                     "creators", "commands", "relays"]))
    for d in dirs:
        for r in census(d):
            print("\t".join(r))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
