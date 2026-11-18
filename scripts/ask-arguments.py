#!/usr/bin/env python3
"""Give every bare `ask query Q of P` the arguments its query declares.

riddlc 2.7.0-20 deprecates the bare form for a query that has fields
(`value-ask-bare-query`): nothing says what is asked. This fills each field
from the message that triggered the clause holding the ask, using the facts
`riddlc dump --json` reports (resolved message, binding, field names and
types), never by parsing RIDDL:

  1. a field of the trigger with the same name and type
  2. a field of the trigger with the same name, or the only one whose name
     ends with it and has its type
  3. the only field of the trigger with the same named type, when no other
     field of the query shares that type
  4. the same three, one level down through a required record field
  5. otherwise a `prompt` naming what is asked

An optional query field that 1-4 cannot fill is `empty` -- not asked by.

Usage:
    ./scripts/ask-arguments.py SWEEP.jsonl [--apply] [--model PATH]

SWEEP.jsonl is `collect-warnings.py` output; only its value-ask-bare-query
sites are touched. Without --apply it prints the plan (one TSV row per
argument: model, file, line, query, field, how, value) and changes nothing.
"""
import json
import re
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_r = os.environ.get("RIDDLC", str(ROOT.parent / "bin" / "riddlc"))
RIDDLC = Path(_r) if os.path.isabs(_r) else (ROOT / _r).resolve()


def dump(model_dir: Path):
    entry = model_dir / (model_dir.name + ".riddl")
    out = subprocess.run([str(RIDDLC), "dump", entry.name, "--json"],
                         cwd=model_dir, capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        raise SystemExit(f"dump failed for {model_dir}: {out.stderr[-500:]}")
    return json.loads(out.stdout)


class Model:
    def __init__(self, nodes):
        self.nodes = nodes
        self.by_path = {n["path"]: n for n in nodes if "path" in n}
        self.fields = defaultdict(list)
        for n in nodes:
            if n["kind"] == "field":
                self.fields[n["parent"]].append(n)
        self.types_by_id = defaultdict(list)
        for n in nodes:
            if n["kind"] in ("type", "record") and "path" in n:
                self.types_by_id[n["id"]].append(n["path"])

    def record_fields(self, field):
        """Fields of a required field's record type, when unambiguous."""
        if field.get("cardinality") != "exactly-one" or field.get("acceptsEmpty"):
            return []
        t = field.get("type", "")
        for kw in ("type ", "record "):
            if t.startswith(kw) and " " not in t[len(kw):]:
                name = t[len(kw):].split(".")[-1]
                paths = self.types_by_id.get(name, [])
                # several definitions share the name: take the one in the
                # nearest enclosing scope of the field that names it, as
                # riddlc's own resolution does
                scope = field["parent"]
                while paths and scope:
                    near = [p for p in paths
                            if p.rsplit(".", 1)[0] == scope]
                    if len(near) == 1:
                        return self.fields.get(near[0], [])
                    scope = scope.rsplit(".", 1)[0] if "." in scope else ""
                if len(paths) == 1:
                    return self.fields.get(paths[0], [])
        return []


def choose(model, qfield, trigger_fields, binding, by_type=True):
    name, typ = qfield["id"], qfield.get("type")

    def pick(cands, prefix):
        same = [f for f in cands if f["id"] == name and f.get("type") == typ]
        if same:
            return f"{prefix}{same[0]['id']}", "name+type"
        named = [f for f in cands if f["id"] == name]
        if named:
            return f"{prefix}{named[0]['id']}", "name"
        suffixed = [f for f in cands if f["id"].endswith(name[0].upper() + name[1:])
                    and f.get("type") == typ]
        if len(suffixed) == 1:
            return f"{prefix}{suffixed[0]['id']}", "suffix+type"
        # a bare TimeStamp or String says nothing about meaning; only a named
        # domain type does
        typed = [f for f in cands if by_type and f.get("type") == typ
                 and typ.startswith(("type ", "record "))]
        if len(typed) == 1:
            return f"{prefix}{typed[0]['id']}", "type"
        return None, None

    v, how = pick(trigger_fields, f"{binding}.")
    if v:
        return v, how
    hits = []
    for f in trigger_fields:
        sub = model.record_fields(f)
        if sub:
            v, how = pick(sub, f"{binding}.{f['id']}.")
            if v:
                hits.append((v, "nested " + how))
    if len(hits) == 1:
        return hits[0]
    # tourId found under both 'tour' and 'departure': prefer the record the
    # field is named for
    stem = name[:-2] if name.endswith("Id") else name
    named = [h for h in hits if h[0].split(".")[-2] == stem]
    if len(named) == 1:
        return named[0]
    return None, None


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    only = args[args.index("--model") + 1] if "--model" in args else None
    sweep = args[0]
    sites = defaultdict(list)
    for line in open(sweep):
        x = json.loads(line)
        if x["rule"] == "value-ask-bare-query":
            if only and x["model"] != only:
                continue
            sites[x["model"]].append(x)
    total = 0
    for mdl, finds in sorted(sites.items()):
        mdir = ROOT / mdl
        model = Model(dump(mdir))
        # a finding's column is the query reference, four past the ask
        want = {(f["file"], f["line"], f["col"] - len("ask ")) for f in finds}
        asks = [n for n in model.nodes if n["kind"] == "ask"
                and (n["file"], n["span"]["start"]["line"],
                     n["span"]["start"]["col"]) in want]
        if len(asks) != len(want):
            print(f"# {mdl}: matched {len(asks)} of {len(want)} sites",
                  file=sys.stderr)
        edits = defaultdict(list)  # file -> [(offset, text)]
        for a in asks:
            clause = model.by_path.get(a["parent"])
            src = (mdir / a["file"]).read_text()
            off = a["span"]["start"]["offset"]
            text = src[off:off + 400]
            # 'ask query <Path> of ...' -- the path ends before ' of '
            assert text.startswith("ask query "), (mdl, a["file"], text[:40])
            qref = text[len("ask query "):].split(" ", 1)[0]
            if "(" in qref:  # already given its arguments
                continue
            qnode = None
            for p, n in model.by_path.items():
                if n["kind"] == "query" and p.endswith("." + qref.split(".")[-1]) \
                        and p.endswith(qref):
                    qnode = n
                    break
            assert qnode, (mdl, qref)
            binding, trig = None, []
            if clause and clause.get("message"):
                binding = clause.get("binding")
                trig = model.fields.get(clause["message"].get("resolved", ""), [])
            parts = []
            qfields = model.fields.get(qnode["path"], [])
            for qf in qfields:
                # origin and destination share a type; type alone cannot
                # tell them apart
                alone = sum(1 for o in qfields
                            if o.get("type") == qf.get("type")) == 1
                v, how = (choose(model, qf, trig, binding, alone) if binding
                          else (None, None))
                # only a field that accepts empty may be left empty; a
                # one-or-more collection must be stated
                optional = bool(qf.get("acceptsEmpty"))
                if v is None:
                    if optional:
                        how, v = "empty (optional)", "empty"
                    else:
                        words = re.sub(r"(?<=[a-z0-9])([A-Z])", r" \1",
                                       qf["id"]).lower()
                        v = f'prompt("the {words} this asks about")'
                        how = "prompt"
                print("\t".join([mdl, a["file"], str(a["span"]["start"]["line"]),
                                 qref, qf["id"], how, v or ""]))
                if v is not None:
                    parts.append(f"{qf['id']} = {v}")
            if parts:
                at = off + len("ask query ") + len(qref)
                edits[a["file"]].append((at, "(" + ", ".join(parts) + ")"))
                total += 1
        if apply:
            for f, es in edits.items():
                p = mdir / f
                s = p.read_text()
                for at, ins in sorted(es, reverse=True):
                    s = s[:at] + ins + s[at:]
                p.write_text(s)
    print(f"# {total} asks given arguments", file=sys.stderr)


if __name__ == "__main__":
    main()
