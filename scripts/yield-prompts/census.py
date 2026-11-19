#!/usr/bin/env python3
"""Census of `stmt-yield-argument-prompt` advisories (BACKLOG #43 step 5).

The advisory fires on a `yield event E(f = prompt("..."))` argument and
suggests stating the value instead: a message or state field, `system.now`,
or an expression -- or dropping the field from the event.

For each advisory this reports, from `riddlc dump --json` alone (no regex
over RIDDL): the clause that yields, its binding and message, the yielded
event's declared type for the argument, and a proposed class:

  NOW    the field is a TimeStamp, and a command clause may read system.now
         (only an event-sourced FOLD may not)
  MSG    the clause's own message carries a field of that name and type:
         <binding>.<field>
  STATE  a record of the yielding entity declares a field of that name
         and type, so the value is state the entity already holds
  OTHER  none of those; needs a reading of the model

Usage:  ./scripts/yield-prompts/census.py [--sweep FILE.jsonl] [--apply] [model ...]
  --sweep  a collect-warnings.py JSONL to take the advisories from
           (default: run collect-warnings.py)
  --apply  rewrite every NOW and MSG site: the prompt node's own span (from
           the dump) is replaced by the fix. A site whose text there is not
           exactly `prompt("...")` is refused and reported, never guessed at.
           STATE and OTHER are never touched: they need a reading.
Writes TSV to stdout; a summary to stderr.
"""
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()
RULE = "stmt-yield-argument-prompt"


def advisories(argv):
    if "--sweep" in argv:
        i = argv.index("--sweep")
        src = open(argv[i + 1]).read()
        del argv[i:i + 2]
    else:
        src = subprocess.run([str(ROOT / "scripts" / "collect-warnings.py"),
                              "--include-patterns"], capture_output=True,
                             text=True, cwd=ROOT).stdout
    out = [json.loads(l) for l in src.splitlines() if l.strip()]
    out = [x for x in out if x.get("rule") == RULE]
    if argv:
        out = [x for x in out if x["model"] in argv]
    return out


def dump(model):
    mdir = ROOT / model
    r = subprocess.run([str(RIDDLC), "dump", mdir.name + ".riddl", "--json"],
                       cwd=mdir, capture_output=True, text=True)
    if not r.stdout.strip():
        raise SystemExit(f"dump failed: {model}\n{r.stderr[-400:]}")
    return json.loads(r.stdout)


def contains(span, line, col):
    s, e = span["start"], span["end"]
    if (line, col) < (s["line"], s.get("col", 0)):
        return False
    return line <= e["line"]


def norm(t):
    return (t or "").replace("type ", "").strip()


def main(argv):
    apply = "--apply" in argv
    if apply:
        argv.remove("--apply")
    adv = advisories(argv)
    edits = defaultdict(list)   # (model, file) -> [(start, end, fix)]
    by_model = defaultdict(list)
    for a in adv:
        by_model[a["model"]].append(a)
    rows, cls = [], Counter()
    for model, items in sorted(by_model.items()):
        nodes = dump(model)
        by_path = {n["path"]: n for n in nodes if "path" in n}
        fields = defaultdict(dict)
        for n in nodes:
            if n["kind"] == "field":
                fields[n["parent"]][n["id"]] = norm(n.get("type"))
        prompts = [n for n in nodes if n["kind"] == "prompt-value"]
        yields = [n for n in nodes if n["kind"] == "yield-statement"]
        for a in items:
            arg = a["message"].split("'")[1]
            p = [n for n in prompts if n["file"].lstrip("./") == a["file"].lstrip("./")
                 and n["span"]["start"]["line"] == a["line"]
                 and a["col"] <= n["span"]["start"].get("col", 0) <= a["endcol"]]
            if len(p) != 1:
                rows.append([model, a["file"], str(a["line"]), arg, "?", "", "", "UNMATCHED", ""])
                cls["UNMATCHED"] += 1
                continue
            clause = by_path.get(p[0]["parent"], {})
            y = [n for n in yields if n["parent"] == p[0]["parent"]
                 and contains(n["span"], a["line"], a["col"])]
            event = y[-1]["message"]["resolved"] if y else ""
            ftype = fields[event].get(arg, "")
            binding = clause.get("binding", "")
            msg = clause.get("message", {}).get("resolved", "")
            mfields = fields.get(msg, {})
            ent = next((by_path[x] for x in reversed(clause.get("ancestors", []))
                        if by_path.get(x, {}).get("kind") == "entity"), None)
            state_hit = ""
            if ent:
                for r in (n for n in nodes if n["kind"] == "record" and n["parent"] == ent["path"]):
                    if fields[r["path"]].get(arg) == ftype:
                        state_hit = r["id"]
                        break
            if ftype == "TimeStamp":
                c, fix = "NOW", "system.now"
            elif binding and mfields.get(arg) == ftype:
                c, fix = "MSG", f"{binding}.{arg}"
            elif state_hit:
                c, fix = "STATE", state_hit
            else:
                c, fix = "OTHER", ""
            cls[c] += 1
            if c in ("NOW", "MSG"):
                sp = p[0]["span"]
                edits[(model, p[0]["file"])].append(
                    (sp["start"]["offset"], sp["end"]["offset"], fix))
            rows.append([model, a["file"], str(a["line"]), arg, ftype,
                         clause.get("id", ""), event.rsplit(".", 1)[-1], c, fix])
    print("\t".join(["model", "file", "line", "arg", "type", "clause", "event", "class", "fix"]))
    for r in rows:
        print("\t".join(r))
    if apply:
        done = refused = 0
        for (model, f), es in sorted(edits.items()):
            path = ROOT / model / f
            txt = path.read_text()
            for start, end, fix in sorted(es, reverse=True):
                old = txt[start:end]
                if not (old.startswith('prompt("') and old.endswith('")')
                        and old.count('"') == 2):
                    print(f"REFUSED {model}/{f}@{start}: {old[:60]!r}", file=sys.stderr)
                    refused += 1
                    continue
                txt = txt[:start] + fix + txt[end:]
                done += 1
            path.write_text(txt)
        print(f"# applied {done}, refused {refused}", file=sys.stderr)
    print(f"# {len(adv)} advisories in {len(by_model)} models: {dict(cls)}", file=sys.stderr)
    if not adv:
        raise SystemExit("no advisories found -- check the sweep is live before believing it")


if __name__ == "__main__":
    main(sys.argv[1:])
