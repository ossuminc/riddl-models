#!/usr/bin/env python3
"""Apply scripts/folds/f3-placement.tsv: move each entity-level clause that
morphs into the handler of every state it is accepted in, and fill the
morph's prompted record arguments from what that state can read.

  f3-apply.py [model-dir ...]        (default: every model in the TSV)

For each row (one clause, its target, its source states):
  * an event-sourced entity's fold carries the command that yields its
    event with it, so the command is accepted where the fold applies;
  * in each source state's copy, a `f = prompt("...")` argument of a morph
    becomes `<binding>.f` when the handled message carries f, else
    `<StateRecord>.f` when that state's record does -- same type, and a
    cardinality the target accepts (never optional into required: that is
    the #44 F3 guard decision, left as a prompt);
  * the clause leaves the entity-level handler.

Facts come from `riddlc dump --json`; only argument lists are read from
source, inside the morph statement's own span. Each model is validated with
--provide-tips afterwards and RESTORED unless it reports zero messages of
every severity. Set RIDDLC to choose the binary (default: riddlc on PATH).
"""
import csv, collections, json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TSV = ROOT / "scripts/folds/f3-placement.tsv"
RIDDLC = os.environ.get("RIDDLC", "riddlc")
IF = re.compile(r'^\s*input-file\s*=\s*"?([^"\s]+)"?', re.M)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PROMPT = re.compile(r'prompt\("(?:[^"\\]|\\.)*"\)$')


def entry(model):
    for c in (ROOT / model).glob("*.conf"):
        m = IF.search(c.read_text())
        return m.group(1) if m else c.stem + ".riddl"


def dump(model):
    r = subprocess.run([RIDDLC, "dump", entry(model), "--json"], cwd=ROOT / model,
                       capture_output=True, text=True)
    return json.loads(r.stdout)


def findings(model):
    r = subprocess.run([RIDDLC, "--provide-tips", "validate", entry(model)], cwd=ROOT / model,
                       capture_output=True, text=True)
    out = ANSI.sub("", r.stdout + r.stderr)
    return [l for l in out.splitlines() if re.match(r"^\[\w+\]", l)]


def base(t):
    return re.sub(r"[?*+]$", "", t.strip())


def compatible(src, tgt):
    if base(src["type"]) != base(tgt["type"]):
        return False
    s, t = src["cardinality"], tgt["cardinality"]
    return s == t or t in ("optional", "zero-or-more") and s == "exactly-one" \
        or t == "zero-or-more" and s == "one-or-more"


def arg_spans(text, start):
    """(name, value, vstart, vend) for each top-level arg of the paren at start."""
    out, depth, q, i, seg = [], 0, False, start + 1, start + 1
    while i < len(text):
        ch = text[i]
        if q:
            if ch == "\\": i += 1
            elif ch == '"': q = False
        elif ch == '"': q = True
        elif ch in "([{": depth += 1
        elif ch in ")]}":
            if depth == 0:
                out.append(seg_arg(text, seg, i)); break
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(seg_arg(text, seg, i)); seg = i + 1
        i += 1
    return [a for a in out if a]


def seg_arg(text, a, b):
    s = text[a:b]
    m = re.match(r"\s*(\w+)\s*=\s*", s)
    if not m: return None
    v0 = a + m.end(); v1 = b
    while v1 > v0 and text[v1 - 1].isspace(): v1 -= 1
    return (m.group(1), text[v0:v1], v0, v1)


def line_start(text, off):
    return text.rfind("\n", 0, off) + 1


def line_after(text, end):
    """A span's end may be the next line's start or the next token: back up
    to the closing brace, then take the rest of its line."""
    while end > 0 and text[end - 1].isspace(): end -= 1
    nl = text.find("\n", end)
    return len(text) if nl < 0 else nl + 1


def body_close(text, start):
    """Offset of the brace closing the first `{` at or after start, skipping
    strings and `|` description lines."""
    i = text.find("{", start); depth = 0
    if i < 0: return None
    while i < len(text):
        ch = text[i]
        if ch == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif ch == "|" and not text[line_start(text, i):i].strip():
            i = text.find("\n", i)
            if i < 0: return None
        elif ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return i
        i += 1
    return None


def apply_model(model, rows, log):
    d = dump(model)
    by = {x["path"]: x for x in d if "path" in x}
    kids = collections.defaultdict(list)
    for x in d:
        if "parent" in x: kids[x["parent"]].append(x)
    fields = collections.defaultdict(dict)
    for x in d:
        if x.get("kind") == "field": fields[x["parent"]][x["id"]] = x
    files = {}
    def src(f):
        if f not in files: files[f] = (ROOT / model / f).read_text()
        return files[f]
    # state -> record path
    state_rec = {}
    for x in d:
        if x.get("kind") != "state": continue
        head = src(x["file"])[x["span"]["start"]["offset"]:x["span"]["end"]["offset"]]
        m = re.search(r"of\s+record\s+([\w.]+)", head)
        rid = m.group(1).split(".")[-1]
        scope = x["parent"].rsplit(".", 1)[0]
        cands = sorted((p for p, n in by.items() if n.get("kind") == "record" and n["id"] == rid
                        and p.startswith(scope)), key=lambda p: (not p.startswith(x["parent"] + "."), len(p)))
        if cands: state_rec[x["path"]] = cands[0]   # else: no carries from it
    # clause -> sources (union over its morph rows)
    moves = collections.OrderedDict()
    for r in rows:
        if r["clause"] not in by:
            log.append(f"  SKIP {r['clause']}: not in dump"); return False
        moves.setdefault(r["clause"], [r["entity"], []])
        for s in r["sources"].split(","):
            sp = r["entity"] + "." + s
            if sp not in by:
                log.append(f"  SKIP {model}: state {s} unknown"); return False
            if sp not in moves[r["clause"]][1]: moves[r["clause"]][1].append(sp)
    # event-sourced: the yielding command travels with its fold
    for cp, (ent, srcs) in list(moves.items()):
        c = by[cp]
        if c["kind"] != "on-event": continue
        ev = c["message"]["resolved"].split(".")[-1]
        h = c["parent"]
        for k in kids[h]:
            if k.get("kind") != "onmessageclause" or k["path"] in moves and k["path"] != cp: continue
            body = src(k["file"])[k["span"]["start"]["offset"]:k["span"]["end"]["offset"]]
            if re.search(r"\byield\s+event\s+(?:[\w.]+\.)?" + ev + r"\b", body):
                moves.setdefault(k["path"], [ent, []])
                for s in srcs:
                    if s not in moves[k["path"]][1]: moves[k["path"]][1].append(s)
    # every moved clause must sit in an entity-level handler
    for cp, (ent, _) in moves.items():
        if by[cp]["parent"].rsplit(".", 1)[0] != ent:
            log.append(f"  SKIP {model}: {cp} is not entity-level"); return False
    morphs = [x for x in d if x.get("kind") == "morph-statement"]
    edits = collections.defaultdict(list)   # file -> (start, end, text)
    inserts = collections.defaultdict(list) # state path -> [clause text]
    carried = prompted = 0
    for cp, (ent, srcs) in moves.items():
        c = by[cp]; text = src(c["file"])
        a, b = line_start(text, c["span"]["start"]["offset"]), line_after(text, c["span"]["end"]["offset"])
        ctext = text[a:b]
        msg = c.get("message", {}).get("resolved")
        mfields = fields.get(msg, {}) if c.get("binding") else {}
        inner = [m for m in morphs if m["file"] == c["file"] and a <= m["span"]["start"]["offset"] < b
                 and "resolved" in m.get("value", {})]
        for s in srcs:
            out = ctext; shift = 0
            sf = fields.get(state_rec.get(s, ""), {})
            rid = state_rec.get(s, "").split(".")[-1]
            reps = []
            for m in inner:
                tf = fields.get(m["value"]["resolved"], {})
                rec = m["value"]["resolved"].split(".")[-1]
                mo = m["span"]["start"]["offset"] - a
                me = m["span"]["end"]["offset"] - a
                p = ctext.find(rec + "(", mo)
                if p < 0 or p > me: continue
                for name, val, v0, v1 in arg_spans(ctext, p + len(rec)):
                    if not PROMPT.match(val) or name not in tf: continue
                    prompted += 1
                    if name in mfields and compatible(mfields[name], tf[name]):
                        reps.append((v0, v1, f"{c['binding']}.{name}"))
                    elif name in sf and compatible(sf[name], tf[name]):
                        reps.append((v0, v1, f"{rid}.{name}"))
            for v0, v1, new in sorted(reps, reverse=True):
                out = out[:v0] + new + out[v1:]
            carried += len(reps)
            inserts[s].append(out)
        edits[c["file"]].append((a, b, ""))
    # insert into each state's handler
    for s, texts in inserts.items():
        st = by[s]; f = st["file"]; text = src(f)
        hs = [k for k in kids[s] if k.get("kind") == "handler"]
        body = "".join(texts)
        if hs:
            h = next((k for k in hs if k.get("initial")), hs[0]) if len(hs) > 1 else hs[0]
            close = body_close(text, h["span"]["start"]["offset"])
            if close is None:
                log.append(f"  SKIP {model}: cannot find the end of handler {h['id']}"); return False
            at = line_start(text, close)
            if text[at:close].strip():
                log.append(f"  SKIP {model}: handler {h['id']} closes mid-line"); return False
            edits[f].append((at, at, body))
        else:
            s0, s1 = st["span"]["start"]["offset"], st["span"]["end"]["offset"]
            head = text[s0:s1]
            m = re.match(r"state\s+(\w+)\s+of\s+record\s+[\w.]+(\s+)with\s*\{", head)
            if not m:
                log.append(f"  SKIP {model}: cannot open state {st['id']}"); return False
            name = st["id"] + "Handler"
            if any(n.get("id") == name for n in by.values()):
                name = st["id"] + "Clauses"
            hb = (f" is {{\n    initial handler {name} is {{\n{body}    }} with {{\n"
                  f"      briefly \"While {st['id']}\"\n      described as {{\n"
                  f"        |The commands and folds accepted while the entity is in {st['id']}.\n"
                  f"      }}\n    }}\n  }} with {{")
            ws0 = s0 + m.start(2)
            edits[f].append((ws0, s0 + m.end(), hb))
    # write, newest offsets first; refuse overlaps
    saved = {}
    for f, es in edits.items():
        es.sort(key=lambda e: (e[0], e[1]), reverse=True)
        for (a1, b1, _), (a2, b2, _) in zip(es, es[1:]):
            if b2 > a1:
                log.append(f"  SKIP {model}: overlapping edits in {f}: {(a2, b2, t2[:40] if (t2 := es[es.index((a2, b2, _))][2]) else "")} vs {(a1, b1)}"); return False
        text = src(f); saved[f] = text
        for a, b, t in es:
            text = text[:a] + t + text[b:]
        (ROOT / model / f).write_text(text)
    bad = findings(model)
    if bad:
        for f, t in saved.items(): (ROOT / model / f).write_text(t)
        log.append(f"  REVERTED {model}: {len(bad)} finding(s): " + "; ".join(bad[:3]))
        return False
    log.append(f"  OK {model}: {len(moves)} clauses moved, {carried} of {prompted} prompts filled")
    return True


def main():
    rows = list(csv.DictReader(TSV.open(), delimiter="\t"))
    want = set(sys.argv[1:])
    by_model = collections.OrderedDict()
    for r in rows:
        if r["sources"] == "-":   # decided: stays in the entity-level handler
            continue
        if not want or r["model"] in want:
            by_model.setdefault(r["model"], []).append(r)
    ok = 0; log = []
    for model, rs in by_model.items():
        if findings(model):
            log.append(f"  SKIP {model}: not clean before"); continue
        ok += apply_model(model, rs, log); print(log[-1], flush=True) if log else None
    print("--- full log ---\n" + "\n".join(log))
    print(f"{ok} of {len(by_model)} models applied")


if __name__ == "__main__":
    main()
