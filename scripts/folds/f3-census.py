#!/usr/bin/env python3
"""Usage: f3-census.py <dir of riddlc dump --json files, named a__b__model.json> <repo root> <out.tsv>

F3 census: every prompted argument of a morph's record constructor,
classified by what the state(s) being left could supply for it.

Facts come from riddlc dump --json (morph target record, handler placement,
record fields with cardinality). Only the constructor's argument list is
read from source, sliced by the morph statement's own span.
"""
import json, pathlib, re, sys, collections, csv

DUMPS = pathlib.Path(sys.argv[1])
ROOT = pathlib.Path(sys.argv[2])
OUT = pathlib.Path(sys.argv[3])
PREFIXES = ("updated", "current", "actual", "latest", "new", "last",
            "pending", "proposed", "revised", "recorded", "draft",
            "preliminary", "partial", "initial", "assigned", "approved", "applied",
            "charged")
PROMPT = re.compile(r'^prompt\("')


def split_args(s):
    out, depth, cur, q = [], 0, "", False
    for ch in s:
        if q:
            cur += ch
            if ch == '"': q = False
            continue
        if ch == '"': q = True
        elif ch in "([{": depth += 1
        elif ch in ")]}": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip(): out.append(cur.strip())
    return out


def ctor_args(text, rec_id):
    i = text.find(rec_id + "(")
    if i < 0: return None
    i += len(rec_id) + 1
    depth, q, j = 1, False, i
    while j < len(text) and depth:
        ch = text[j]
        if q:
            if ch == '"': q = False
        elif ch == '"': q = True
        elif ch == "(": depth += 1
        elif ch == ")": depth -= 1
        j += 1
    args = {}
    for a in split_args(text[i:j - 1]):
        if "=" in a:
            k, v = a.split("=", 1); args[k.strip()] = v.strip()
    return args


def base(t):
    return re.sub(r"[?*+]$", "", t.strip())


rows, totals = [], collections.Counter()
for dump in sorted(DUMPS.glob("*.json")):
    model = dump.stem.replace("__", "/")
    d = json.loads(dump.read_text())
    by_path = {x["path"]: x for x in d if "path" in x}
    fields = collections.defaultdict(dict)
    for x in d:
        if x.get("kind") == "field":
            fields[x["parent"]][x["id"]] = x
    states_of = collections.defaultdict(list)
    state_rec = {}
    for x in d:
        if x.get("kind") != "state": continue
        states_of[x["parent"]].append(x["path"])
        src = (ROOT / model / x["file"]).read_text()
        head = src[x["span"]["start"]["offset"]:x["span"]["end"]["offset"]]
        m = re.search(r"of\s+record\s+([\w.]+)", head)
        if not m: continue
        rid = m.group(1).split(".")[-1]
        ent = x["parent"]
        cands = [p for p, n in by_path.items() if n.get("kind") == "record"
                 and n["id"] == rid and p.startswith(ent.rsplit(".", 1)[0])]
        cands.sort(key=lambda p: (not p.startswith(ent + "."), len(p)))
        if cands: state_rec[x["path"]] = cands[0]
    for x in d:
        if x.get("kind") != "morph-statement": continue
        totals["morphs"] += 1
        anc = x["ancestors"]
        handler = next((a for a in reversed(anc)
                        if by_path.get(a, {}).get("kind") == "handler"), None)
        clause = next((a for a in reversed(anc) if by_path.get(a, {}).get("kind")
                       in ("on-init", "onmessageclause", "on-event", "on-other")), None)
        ckind = by_path.get(clause, {}).get("kind")
        hp = by_path.get(handler, {}).get("parent")
        ent = x["target"]["resolved"]
        if ckind == "on-init" and by_path.get(hp, {}).get("kind") == "entity":
            placement, sources = "creation", []
        elif by_path.get(hp, {}).get("kind") == "state":
            placement, sources = "state", [hp]
        else:
            tgt = x.get("state", {}).get("resolved")
            placement, sources = "entity", [s for s in states_of.get(ent, []) if s != tgt]
        if "resolved" not in x.get("value", {}):
            totals["morph-by-binding"] += 1; continue
        rec = x["value"]["resolved"]
        src = (ROOT / model / x["file"]).read_text()
        text = src[x["span"]["start"]["offset"]:x["span"]["end"]["offset"]]
        args = ctor_args(text, rec.split(".")[-1])
        if args is None:
            totals["unparsed"] += 1; continue
        tf = fields.get(rec, {})
        for name, val in args.items():
            if not PROMPT.match(val): continue
            totals["prompted"] += 1
            t = tf.get(name)
            if t is None:
                totals["no-target-field"] += 1; continue
            tcard, tbase = t["cardinality"], base(t["type"])
            if placement == "creation":
                cls, detail = "creation", ""
            else:
                per = []
                for s in sources:
                    sf = fields.get(state_rec.get(s, ""), {})
                    hit = None
                    names = [name] + [p + name[0].upper() + name[1:] for p in PREFIXES]
                    for n in names:
                        f = sf.get(n)
                        if f is None: continue
                        if base(f["type"]) != tbase:
                            hit = hit or ("type-differs", n); continue
                        scard = f["cardinality"]
                        if scard == tcard or (tcard == "zero-or-more") or \
                           (tcard == "optional" and scard == "exactly-one"):
                            hit = ("carry", n); break
                        hit = ("narrowing", n, scard); break
                    per.append((s.split(".")[-1], hit))
                kinds = {h[0] if h else "none" for _, h in per}
                if not per: cls = "no-source-state"
                elif kinds == {"carry"}: cls = "carry"
                elif "narrowing" in kinds and kinds <= {"narrowing", "carry"}:
                    cls = "narrowing"
                elif kinds == {"none"}: cls = "none"
                elif kinds == {"type-differs"} or kinds == {"type-differs", "none"}:
                    cls = "type-differs"
                else: cls = "mixed"
                detail = "; ".join(f"{s}:{h[1] + ('/' + h[2] if len(h) > 2 else '') if h else '-'}"
                                   for s, h in per)
            totals[cls] += 1
            rows.append(dict(model=model, file=x["file"], line=x["span"]["start"]["line"],
                             entity=ent.split(".")[-1], clause=(clause or "").split(".")[-1],
                             placement=placement, nsrc=len(sources), field=name,
                             target_card=tcard, cls=cls, detail=detail))

with OUT.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t")
    w.writeheader(); w.writerows(rows)
print(dict(totals))
m = collections.Counter((r["cls"], r["placement"]) for r in rows)
for k, v in sorted(m.items()): print(k, v)
print("models with narrowing:", len({r["model"] for r in rows if r["cls"] == "narrowing"}))
