#!/usr/bin/env python3
"""Route each delegated creation answer back to the application that asked.

riddl 2.8.5 reports `stmt-initiate-id-unused` at a delegating `create` when a
sender of the creation command (here always an application context) has no
`on event` clause for the creation event. The shape ruled in (Reid,
2026-11-24) is the outward boundary relay plus a group output:

  creating context C
    split S        outlet S To<E>Answer; its existing `on event E` clause
                   gains `send <b> to outlet S To<E>Answer`
    C              inlet <E>AnswerIn, outlet <E>AnswerOut, a boundary clause
                   relaying E from one to the other, and the intra-context
                   connector '<E> Answer Relay'
  application A
    group G        output <E>View presents event <E>, beside the input that
                   acquires the command
    A              inlet App<E>Answer, a clause putting E to the output, and
                   the persistent connector '<E> Answer' from C

Everything is located with `riddlc dump --json`; text is only inserted at the
offsets it reports. A site whose pieces cannot all be found is REFUSED, not
guessed. Usage:

  wire-creation-answers.py <sites.jsonl> [--dry-run]

where each line is a collect-warnings.py record for stmt-initiate-id-unused.
"""
import json, os, re, subprocess, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RIDDLC = os.path.expanduser(os.environ.get("RIDDLC", "riddlc"))
INPUT_KINDS = {"input", "form", "text", "button", "picklist", "selector", "item", "voice", "gesture", "gaze"}
MSG = re.compile(r"in Event '(\w+)', but Context '(\w+)' sends Command '(\w+)'")


def entry_of(model_dir):
    for f in sorted(os.listdir(model_dir)):
        if f.endswith(".conf"):
            m = re.search(r'input-file\s*=\s*"([^"]+)"', open(os.path.join(model_dir, f)).read())
            if m:
                return m.group(1)
    raise SystemExit(f"no .conf entry in {model_dir}")


def dump(model_dir, entry):
    out = subprocess.run([RIDDLC, "dump", entry, "--json"], cwd=model_dir,
                         capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        raise SystemExit(f"dump failed in {model_dir}: {out.stderr[-500:]}")
    return json.loads(out.stdout)


def rel(path, base):
    """`path` written from inside `base` (both dotted)."""
    return path[len(base) + 1:] if path.startswith(base + ".") else path


def plan_model(model, sites, nodes):
    model_dir = os.path.join(ROOT, model)
    by_path = {n["path"]: n for n in nodes if "path" in n}
    ids = {n.get("id") for n in nodes}
    contexts = {n["path"] for n in nodes if n["kind"] == "context"}
    edits = collections.defaultdict(list)   # file -> [(offset, text)]
    refused, planned = [], []
    src_cache = {}

    def src(f):
        if f not in src_cache:
            src_cache[f] = open(os.path.join(model_dir, f), "rb").read().decode("utf-8")
        return src_cache[f]

    def line_start(f, off):
        return src(f).rfind("\n", 0, off) + 1

    def after_header(n):
        """offset just after the `is {` line that opens node n."""
        s = src(n["file"])
        return s.index("\n", s.index("{", n["span"]["start"]["offset"])) + 1

    for site in sites:
        m = MSG.search(site["message"])
        if not m:
            refused.append((site, "message shape")); continue
        ev, app, cmd = m.groups()
        # creating context: the context ancestor of the create at this line
        creates = [n for n in nodes if n["kind"] == "create" and n["file"] == site["file"]
                   and n["span"]["start"]["line"] in (site["line"], site["line"] + 1)]
        if len(creates) != 1:
            refused.append((site, f"{len(creates)} create nodes at line")); continue
        ctx = [a for a in creates[0]["ancestors"] if a in contexts]
        if not ctx:
            refused.append((site, "no context ancestor")); continue
        C = ctx[-1]
        evs = [n for n in nodes if n["kind"] == "event" and n["id"] == ev and n["path"].startswith(C + ".")]
        if len(evs) != 1:
            refused.append((site, f"{len(evs)} events named {ev} in {C}")); continue
        E = evs[0]["path"]
        # the split clause that already receives E
        clauses = [n for n in nodes if n["kind"] == "on-event"
                   and n.get("message", {}).get("resolved") == E
                   and by_path.get(by_path.get(n["parent"], {}).get("parent", ""), {}).get("kind") in ("split", "flow", "router")
                   and by_path[by_path[n["parent"]]["parent"]]["parent"] == C]
        if len(clauses) > 1:
            # several fan-outs see it; the entity's own <Entity>EventSplit owns its events
            own = E.split(".")[-2] + "EventSplit"
            clauses = [n for n in clauses if by_path[n["parent"]]["parent"].endswith("." + own)]
        if len(clauses) != 1:
            refused.append((site, f"{len(clauses)} split clauses for {ev} in {C}")); continue
        clause = clauses[0]
        split = by_path[by_path[clause["parent"]]["parent"]]
        bound = clause.get("binding") or ev[0].lower() + ev[1:]
        handlers = [n for n in nodes if n["kind"] == "handler" and n["parent"] == C]
        apps = [p for p in contexts if p.split(".")[-1] == app]
        if len(handlers) != 1 or len(apps) != 1:
            refused.append((site, f"{len(handlers)} boundary handlers, {len(apps)} apps")); continue
        hC = handlers[0]
        A = apps[0]
        hA = [n for n in nodes if n["kind"] == "handler" and n["parent"] == A]
        inputs = [n for n in nodes if n["kind"] in INPUT_KINDS and n["path"].startswith(A + ".")
                  and re.search(r"acquires\s+command\s+([\w.]+)",
                                src(n["file"])[n["span"]["start"]["offset"]:n["span"]["end"]["offset"]])
                  and re.search(r"acquires\s+command\s+([\w.]+)",
                                src(n["file"])[n["span"]["start"]["offset"]:n["span"]["end"]["offset"]]
                                ).group(1).split(".")[-1] == cmd]
        conns = [n for n in nodes if n["kind"] == "connector"
                 and n.get("from", {}).get("resolved", "").startswith(A + ".")]
        if len(hA) != 1 or len(inputs) != 1 or not conns:
            refused.append((site, f"{len(hA)} app handlers, {len(inputs)} inputs, {len(conns)} app connectors")); continue
        hA, inp = hA[0], inputs[0]
        anchor = min(conns, key=lambda n: n["span"]["start"]["offset"])
        D = anchor["parent"]          # where the app's own connectors live
        group = inp["parent"]

        so, ci, co = f"{split['id']}To{ev}Answer", f"{ev}AnswerIn", f"{ev}AnswerOut"
        ai, out = f"App{ev}Answer", f"{ev}View"
        relay, xconn = f"{ev} Answer Relay", f"{ev} Answer"
        clash = [x for x in (so, ci, co, ai, out, relay, xconn) if x in ids]
        if clash:
            refused.append((site, f"names already declared: {clash}")); continue
        eC, eA, eD = rel(E, C), rel(E, A.rsplit(".", 1)[0]), rel(E, D)
        word = re.sub(r"(?<!^)([A-Z])", r" \1", ev).lower()

        cname = C.split(".")[-1]
        f = hC["file"]
        ind = " " * (hC["span"]["start"]["col"] - 1)
        hs = line_start(f, hC["span"]["start"]["offset"])
        here = [n for n in nodes if n["kind"] == "on-event" and n["parent"] == hC["path"]
                and n.get("message", {}).get("resolved") == E]
        if here:
            # the boundary already receives E (it relays it elsewhere): the
            # answer is one more send from that clause, and nothing else in C
            b = here[0].get("binding") or bound
            close = src(f).rfind("}", 0, here[0]["span"]["end"]["offset"])
            cind = " " * (here[0]["span"]["start"]["col"] + 1)
            edits[f].append((hs, f"{ind}outlet {co} is event {eC}\n"))
            edits[f].append((line_start(f, close), f"{cind}send {b} to outlet {cname}.{co}\n"))
        else:
            # 1. split: outlet + send at the end of the E clause
            f = split["file"]
            sind = " " * (split["span"]["start"]["col"] + 1)
            edits[f].append((after_header(split), f"{sind}outlet {so} is event {rel(E, split['path'])}\n"))
            if split["kind"] == "flow":
                # a second outlet makes the flow a split; its ascription follows
                ss = split["span"]["start"]["offset"]
                hdr = src(f)[ss:src(f).index("{", ss)]
                if hdr.count(" as flow ") != 1:
                    refused.append((site, f"flow header without one 'as flow': {hdr!r}")); continue
                edits[f].append((ss + hdr.index(" as flow "), "\0REPLACE as flow \0 as split "))
            close = src(f).rfind("}", 0, clause["span"]["end"]["offset"])
            cind = " " * (clause["span"]["start"]["col"] + 1)
            edits[f].append((line_start(f, close), f"{cind}send {bound} to outlet {so}\n"))
            # 2. creating context: ports, relay connector, boundary clause
            f = hC["file"]
            edits[f].append((hs,
                f"{ind}inlet {ci} is event {eC}\n"
                f"{ind}outlet {co} is event {eC}\n"
                f"{ind}connector '{relay}' is from outlet {rel(split['path'], C.rsplit('.', 1)[0])}.{so} "
                f"to inlet {cname}.{ci} with {{\n"
                f"{ind}  briefly \"The {word} answer, on its way out of {cname}\"\n{ind}}}\n"))
            edits[f].append((after_header(hC),
                f"{ind}  on {bound}: event {eC} is {{\n"
                f"{ind}    send {bound} to outlet {cname}.{co}\n{ind}  }}\n"))
        # 3. application: output beside the input, inlet, clause, connector
        f = inp["file"]
        ind = " " * (inp["span"]["start"]["col"] - 1)
        edits[f].append((inp["span"]["end"]["offset"],
            f"{ind}output {out} presents event {eA} with {{\n"
            f"{ind}  briefly \"The {word} answer\"\n"
            f"{ind}  described as {{\n"
            f"{ind}    |What {cmd} brought into being, with the id it was given.\n"
            f"{ind}  }}\n{ind}}}\n"))
        f = hA["file"]
        ind = " " * (hA["span"]["start"]["col"] - 1)
        edits[f].append((line_start(f, hA["span"]["start"]["offset"]),
            f"{ind}inlet {ai} is event {eA}\n"))
        edits[f].append((after_header(hA),
            f"{ind}  on {bound}: event {eA} is {{\n"
            f"{ind}    put {bound} to output {rel(group, A.rsplit('.', 1)[0])}.{out}\n{ind}  }}\n"))
        f = anchor["file"]
        ind = " " * (anchor["span"]["start"]["col"] - 1)
        edits[f].append((line_start(f, anchor["span"]["start"]["offset"]),
            f"{ind}persistent connector '{xconn}' is from outlet {rel(C, D)}.{co} "
            f"to inlet {rel(A, D)}.{ai} with {{\n"
            f"{ind}  briefly \"The {word} answer, back to the screen that issued {cmd}\"\n{ind}}}\n"))
        ids.update((so, ci, co, ai, out, relay, xconn))
        planned.append((site, f"{C.split('.')[-1]} -> {app}: {ev} via {split['id']}"))
    return edits, planned, refused, src_cache


def main():
    sites = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    dry = "--dry-run" in sys.argv
    by_model = collections.defaultdict(list)
    for s in sites:
        by_model[s["model"]].append(s)
    total_p, total_r = 0, 0
    for model, ss in sorted(by_model.items()):
        mdir = os.path.join(ROOT, model)
        nodes = dump(mdir, entry_of(mdir))
        edits, planned, refused, src = plan_model(model, ss, nodes)
        for s, why in planned:
            print(f"PLAN   {model}: {why}")
        for s, why in refused:
            print(f"REFUSE {model} {s['file']}:{s['line']}: {why}")
        total_p += len(planned); total_r += len(refused)
        if refused or dry:
            continue                       # a model is wired whole or not at all
        for f, es in edits.items():
            text = src[f]
            for off, ins in sorted(set(es), key=lambda e: -e[0]):
                if ins.startswith("\0REPLACE"):
                    old, new = ins.split("\0")[1:]
                    old = old[len("REPLACE"):]
                    assert text[off:off + len(old)] == old, (f, off)
                    text = text[:off] + new + text[off + len(old):]
                else:
                    text = text[:off] + ins + text[off:]
            open(os.path.join(mdir, f), "w").write(text)
    print(f"planned {total_p}, refused {total_r}")


if __name__ == "__main__":
    main()
