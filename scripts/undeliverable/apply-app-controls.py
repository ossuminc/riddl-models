#!/usr/bin/env python3
"""BACKLOG #43 step 3, rule (a): give the application a control for each
undelivered command it already has an outlet for.

Reads `step3-verdicts.tsv` (one row per undeliverable context command clause,
verdict a/b/c) and acts on the `a` rows only. For each, from `riddlc dump
--json` alone (no regex over RIDDL):

  * the application context whose outlet carries the command and is connected
    to the handling context (exactly one is required, else the site is refused)
  * that app's screen group, or none

and inserts

    input <Command>Input acquires command <path> with { briefly ... }

into the group, as whole lines before the group's first input. An app with no
group gets `group <App minus "App">Screen is { ... }` before its first outlet,
worded like the corpus's existing screens. The command path is the message's
resolved path relative to the app's parent. Indentation is left to prettify
(`sbt r`), which is run afterwards anyway.

Refuses (reports, never guesses): a site with zero or several app outlets, a
name already declared in the model, an app group with no inputs in it.

Usage:  apply-app-controls.py [--apply] [model ...]
Without --apply it reports the plan only.
"""
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()
VERDICTS = Path(__file__).resolve().parent / "step3-verdicts.tsv"


def words(ident):
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", ident)
    s = " ".join(p if p.isupper() and len(p) > 1 else p.lower() for p in parts)
    return s[:1].upper() + s[1:]


def dump(model_dir):
    conf = next(model_dir.glob("*.conf"))
    entry = re.search(r'input-file\s*=\s*"([^"]+)"', conf.read_text()).group(1)
    p = subprocess.run([str(RIDDLC), "dump", entry, "--json"], cwd=model_dir,
                       capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        sys.exit(f"dump failed for {model_dir}: {p.stderr[-400:]}")
    return json.loads(p.stdout)


def expand(byp, alts, seen):
    out = set()
    for a in alts or []:
        r = a["resolved"]
        if r in seen:
            continue
        seen.add(r)
        t = byp.get(r)
        out |= expand(byp, t["alternation"], seen) if t and t.get("alternation") else {r}
    return out


def carries(byp, port):
    t = port.get("type") or {}
    if t.get("alternation"):
        return expand(byp, t["alternation"], set())
    tn = byp.get(t.get("resolved"))
    if tn and tn.get("alternation"):
        return expand(byp, tn["alternation"], set())
    return {t.get("resolved")}


def relative(path, base):
    p, b = path.split("."), base.split(".")
    i = 0
    while i < len(b) and i < len(p) - 1 and p[i] == b[i]:
        i += 1
    return ".".join(p[i:])


def input_lines(name, ref, cmd):
    w = words(cmd).lower()
    return [
        f"input {name} acquires command {ref} with {{",
        f'  briefly "{words(cmd)} control"',
        "  described as {",
        f"    |The control through which a user submits the {w} request.",
        "  }",
        "}",
    ]


def main():
    argv = sys.argv[1:]
    apply = "--apply" in argv
    only = {a.rstrip("/") for a in argv if not a.startswith("--")}
    rows = [r for r in csv.DictReader(open(VERDICTS), delimiter="\t") if r["verdict"] == "a"]
    by_model = defaultdict(list)
    for r in rows:
        if not only or r["model"] in only:
            by_model[r["model"]].append(r)
    tally, refused = Counter(), []
    for model, rs in sorted(by_model.items()):
        md = ROOT / model
        nodes = dump(md)
        byp = {n["path"]: n for n in nodes if "path" in n}
        declared = Counter(n.get("id") for n in nodes)
        conns = defaultdict(list)
        for n in nodes:
            if n["kind"] == "connector":
                conns[n["from"]["resolved"]].append(n["to"]["resolved"])
        apps = {n["path"] for n in nodes if n["kind"] == "context" and n.get("intention") == "Application"}
        app_outlets = [n for n in nodes if n["kind"] == "outlet" and n["parent"] in apps]
        # (file, line) -> list of lines to insert before that line
        inserts = defaultdict(list)
        new_groups = {}  # app path -> (file, line, group name, [input lines])
        for r in rs:
            def is_site(n):
                if n["kind"] != "onmessageclause":
                    return False
                if not n["message"]["resolved"].endswith("." + r["command"]):
                    return False
                h = byp.get(n["parent"], {})
                c = byp.get(h.get("parent"), {})
                return h.get("kind") == "handler" and c.get("kind") == "context" \
                    and c.get("id") == r["context"]
            found = [n for n in nodes if is_site(n)]
            if len(found) != 1:
                refused.append((model, r["command"], f"{len(found)} matching clauses")); continue
            clause = found[0]
            msg = clause["message"]["resolved"]
            ctx = byp[byp[clause["parent"]]["parent"]]["path"]
            outs = [o for o in app_outlets if msg in carries(byp, o)
                    and any(t.startswith(ctx + ".") for t in conns[o["path"]])]
            if len(outs) != 1:
                refused.append((model, r["command"], f"{len(outs)} connected app outlets")); continue
            app = outs[0]["parent"]
            cmd = msg.split(".")[-1]
            name = cmd + "Input"
            if declared[name]:
                refused.append((model, r["command"], f"{name} already declared")); continue
            declared[name] += 1
            ref = relative(msg, byp[app]["parent"])
            lines = input_lines(name, ref, cmd)
            groups = [n for n in nodes if n["kind"] == "group" and n["parent"] == app]
            if groups:
                g = groups[0]
                ins = [n for n in nodes if n["kind"] == "input" and n["parent"] == g["path"]]
                if not ins:
                    refused.append((model, r["command"], "group has no inputs")); continue
                first = min(ins, key=lambda n: n["span"]["start"]["offset"])
                inserts[(first["file"], first["span"]["start"]["line"])].extend(lines)
                tally["into existing group"] += 1
            else:
                if app not in new_groups:
                    gname = byp[app]["id"].removesuffix("App") + "Screen"
                    if declared[gname]:
                        refused.append((model, r["command"], f"group {gname} already declared")); continue
                    declared[gname] += 1
                    first_out = min((o for o in app_outlets if o["parent"] == app),
                                    key=lambda n: n["span"]["start"]["offset"])
                    new_groups[app] = (first_out["file"], first_out["span"]["start"]["line"], gname, [])
                new_groups[app][3].extend(lines)
                tally["into new group"] += 1
        for app, (f, line, gname, lines) in new_groups.items():
            dom = words(byp[app]["id"].removesuffix("App")).lower()
            inserts[(f, line)].extend(
                [f"group {gname} is {{"] + ["  " + l for l in lines] + [
                 "} with {",
                 f'  briefly "{words(gname.removesuffix("Screen"))} screen"',
                 "  described as {",
                 "    |The screen through which users act on this domain.",
                 "  }",
                 "}"])
            tally["new groups"] += 1
        if apply:
            by_file = defaultdict(list)
            for (f, line), lines in inserts.items():
                by_file[f].append((line, lines))
            for f, items in by_file.items():
                p = md / f
                text = p.read_text().split("\n")
                for line, lines in sorted(items, reverse=True):
                    indent = re.match(r"\s*", text[line - 1]).group(0)
                    text[line - 1:line - 1] = [indent + l for l in lines]
                p.write_text("\n".join(text))
        tally["models"] += 1
    for k, v in tally.items():
        print(f"{v}\t{k}", file=sys.stderr)
    print(f"{len(refused)}\trefused", file=sys.stderr)
    for x in refused:
        print("REFUSED\t" + "\t".join(x))


if __name__ == "__main__":
    main()
