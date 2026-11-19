#!/usr/bin/env python3
"""BACKLOG #43: a projector's `on event E` clause that nothing can deliver
because the split feeding it never routes E there.

Measured 2026-11-19 on -27: all 37 such sites are fed by a split outlet whose
type CARRIES E, but the split's handler has no clause sending E to that
outlet -- the split's routing table was not updated when E was added. The fix
is the table's own shape: in the split, `send` E to every outlet whose
projector handles it. An existing clause for E gains the sends; otherwise a
new `on <e>: event E is { send ... }` clause is added before the split's
first clause. Works from `riddlc dump --json`; inserts whole lines.

Refuses a site whose feeder is not a split, or whose feeding outlet does not
carry E.

Usage:  route-split-events.py --sweep FILE.jsonl [--apply] [model ...]
"""
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


def lc(s):
    return s[:1].lower() + s[1:]


def rel(path, scope):
    p, b = path.split("."), scope.split(".")
    i = 0
    while i < len(b) and i < len(p) - 1 and p[i] == b[i]:
        i += 1
    return ".".join(p[i:])


def dump(md):
    conf = next(md.glob("*.conf"))
    entry = re.search(r'input-file\s*=\s*"([^"]+)"', conf.read_text()).group(1)
    p = subprocess.run([str(RIDDLC), "dump", entry, "--json"], cwd=md,
                       capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        sys.exit(f"dump failed for {md}")
    return json.loads(p.stdout)


def main():
    argv = sys.argv[1:]
    apply = "--apply" in argv
    sweep = argv[argv.index("--sweep") + 1]
    only = {a.rstrip("/") for a in argv if not a.startswith("--") and a != sweep}
    sites = defaultdict(list)
    for x in map(json.loads, open(sweep)):
        if x["rule"] == "msg-clause-undeliverable" and "of Projector '" in x["message"] \
                and "handles Event" in x["message"] and (not only or x["model"] in only):
            sites[x["model"]].append(x)
    tally, refused = Counter(), []
    for model, ss in sorted(sites.items()):
        md = ROOT / model
        nodes = dump(md)
        byp = {n["path"]: n for n in nodes if "path" in n}
        kids = defaultdict(list)
        for n in nodes:
            kids[n.get("parent")].append(n)
        conn_to = defaultdict(list)
        for n in nodes:
            if n["kind"] == "connector":
                conn_to[n["to"]["resolved"]].append(n)

        def expand(alts, seen):
            out = set()
            for a in alts or []:
                r = a["resolved"]
                if r in seen:
                    continue
                seen.add(r)
                t = byp.get(r)
                out |= expand(t["alternation"], seen) if t and t.get("alternation") else {r}
            return out

        def carries(port):
            t = port.get("type") or {}
            if t.get("alternation"):
                return expand(t["alternation"], set())
            tn = byp.get(t.get("resolved"))
            return expand(tn["alternation"], set()) if tn and tn.get("alternation") else {t.get("resolved")}

        routes = defaultdict(list)  # (split path, event) -> [outlet ids]
        for s in ss:
            cl = [n for n in nodes if n["kind"] == "on-event" and n["file"].endswith(s["file"])
                  and n["span"]["start"]["line"] == s["line"]]
            if len(cl) != 1:
                refused.append((model, s["file"], s["line"], "clause not located")); continue
            ev = cl[0]["message"]["resolved"]
            proj = next(byp[a] for a in reversed(cl[0]["ancestors"]) if byp.get(a, {}).get("kind") == "projector")
            fed = []
            for i in kids[proj["path"]]:
                if i["kind"] != "inlet" or ev not in carries(i):
                    continue
                for c in conn_to[i["path"]]:
                    o = byp[c["from"]["resolved"]]
                    owner = byp[o["parent"]]
                    if owner["kind"] in ("split", "streamlet") and ev in carries(o):
                        fed.append((owner["path"], o["id"]))
            if len(fed) != 1:
                refused.append((model, proj["id"], ev.split(".")[-1], f"{len(fed)} split feeders")); continue
            if fed[0][1] not in routes[(fed[0][0], ev)]:
                routes[(fed[0][0], ev)].append(fed[0][1])
        ops = defaultdict(list)  # file -> [(line, lines)]
        for (sp, ev), outs in routes.items():
            handler = [h for h in kids[sp] if h["kind"] == "handler"]
            if len(handler) != 1:
                refused.append((model, sp, ev, f"{len(handler)} handlers in split")); continue
            clauses = [n for n in kids[handler[0]["path"]] if n["kind"] in ("on-event", "onmessageclause", "on-other")]
            mine = [n for n in clauses if n.get("message", {}).get("resolved") == ev]
            if mine:
                b = mine[0].get("binding")
                if not b:
                    refused.append((model, sp, ev, "existing clause has no binding")); continue
                ops[mine[0]["file"]].append((mine[0]["span"]["start"]["line"] + 1,
                                             [f"send {b} to outlet {o}" for o in outs]))
                tally["sends added to existing clauses"] += len(outs)
            else:
                b = lc(ev.split(".")[-1])
                first = min(clauses, key=lambda n: n["span"]["start"]["offset"])
                ops[first["file"]].append((first["span"]["start"]["line"],
                                           [f"on {b}: event {rel(ev, sp)} is {{"]
                                           + [f"  send {b} to outlet {o}" for o in outs] + ["}"]))
                tally["clauses added"] += 1
            tally["routes"] += len(outs)
        if apply:
            for f, items in ops.items():
                p = md / f
                text = p.read_text().split("\n")
                for line, lines in sorted(items, key=lambda t: -t[0]):
                    ind = re.match(r"\s*", text[line - 1]).group(0)
                    text[line - 1:line - 1] = [ind + l for l in lines]
                p.write_text("\n".join(text))
        tally["models"] += 1
    for k, v in sorted(tally.items()):
        print(f"{v}\t{k}", file=sys.stderr)
    print(f"{len(refused)}\trefused", file=sys.stderr)
    for r in refused:
        print("REFUSED\t" + "\t".join(map(str, r)))


if __name__ == "__main__":
    main()
