#!/usr/bin/env python3
"""Put a projector between an entity's events and a repository's inlet.

Reid's rule: **a repository has command and query inlets and result outlets, and
nothing else.** It does not process events; it stores data, and that storing IS
the effect. Turning an entity event into a repository command is the PROJECTOR's
job.

Every fact used here comes from `riddlc dump --json`, never from a text search:
which inlets carry events (`type.carries`), the union's members already resolved
(`type.alternation`), which `Persist` commands a repository declares, each one's
id field and cardinality, and the connector that feeds the inlet. The only text
work is inserting at anchors the projection located.

Per repository R in context C, fed from outlet O:

  1. `type <R>Command is one of { <R's Persist commands> }` at context scope
  2. R's event inlet becomes `inlet <R>From<E>Projection is type <R>Command`
  3. a new `projector <E>Projection as flow`, with a clause per union member
     that HAS a `Persist<member>`, each telling it
  4. the feeding connector is repointed to the projector, and a second connector
     carries the projector's commands to R

**Members with no `Persist` command get `on other`, not an invented command.**
They are almost all `<Command>Rejected` events: a rejection is not a state change
to store, so telling a repository to persist one would be modelling a write that
should not happen. `on other` states the policy for them honestly, and the
author's ruling allows exactly that ("add an `on other` clause if anything
arriving should be handled generically").

Skips any repository fed by a projector already -- there the projector exists and
must be changed to emit commands, which is a different edit.

Usage:  ./scripts/repo-event-inlet-to-projector.py <model-dir> [--dry-run]
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


def main():
    dry = "--dry-run" in sys.argv
    arg = [a for a in sys.argv[1:] if a != "--dry-run"][0]
    d = (ROOT / arg).resolve()
    entry = entry_of(d)
    nodes = dump(d, entry)
    byparent, bypath = defaultdict(list), {}
    for n in nodes:
        byparent[n.get("parent")].append(n)
        if n.get("path"):
            bypath[n["path"]] = n
    conns = [n for n in nodes if n.get("kind") == "connector"]

    plans = []
    for r in [n for n in nodes if n.get("kind") == "repository"]:
        kids = byparent[r["path"]]
        persist = {k["id"][7:]: k for k in kids
                   if k.get("kind") == "command" and k["id"].startswith("Persist")}
        if not persist:
            continue
        for inl in kids:
            if inl.get("kind") != "inlet" or (inl.get("type") or {}).get("carries") != "Event":
                continue
            feed = [c for c in conns if (c.get("to") or {}).get("resolved") == inl["path"]]
            if not feed:
                continue
            src = (feed[0].get("from") or {}).get("resolved", "")
            owner = bypath.get(".".join(src.split(".")[:-1]))
            if owner and owner.get("kind") == "projector":
                print(f"  SKIP {r['id']}/{inl['id']}: fed by projector "
                      f"{owner['id']} -- that projector must emit commands instead")
                continue
            # Name the projector from the REPOSITORY, not the union's parent:
            # several unions are declared at CONTEXT scope, which produced
            # `FrontOfHouseProjection` and made MenuItem and MenuRelease collide
            # on one `MenuManagementProjection`.
            ent = re.sub(r"Repository$", "", r["id"])
            # Keep each member's reference AS WRITTEN so the qualifier resolves
            # from wherever the clause ends up.
            members = [m["ref"] for m in inl["type"].get("alternation", [])]
            # The Persist command's id field and the event's are NOT always
            # spelled the same (DeliveryOrder's events carry `deliveryId` while
            # PersistX takes `deliveryOrderId`), so resolve the SOURCE field per
            # event instead of assuming `F = <binder>.F`.
            idf, srcf, extra = {}, {}, {}
            evfields = {}
            for m in inl["type"].get("alternation", []):
                ev = bypath.get(m["resolved"])
                if ev:
                    evfields[m["ref"].split(".")[-1]] = [
                        k["id"] for k in byparent[ev["path"]] if k.get("kind") == "field"]
            for e, cmd in persist.items():
                cf = [k["id"] for k in byparent[cmd["path"]] if k.get("kind") == "field"]
                idf[e] = cf[0] if cf else None
                extra[e] = cf[1:]
                have_f = evfields.get(e, [])
                srcf[e] = (idf[e] if idf[e] in have_f
                           else (have_f[0] if have_f else idf[e]))
            plans.append(dict(repo=r, inlet=inl, conn=feed[0], ent=ent,
                              members=members, persist=persist, idf=idf,
                              srcf=srcf, extra=extra,
                              ctx=r["parent"].split(".")[-1], file=r["file"]))

    if not plans:
        print("  nothing to do")
        return

    for p in plans:
        R, ent, ctx = p["repo"]["id"], p["ent"], p["ctx"]
        proj = f"{ent}Projection"
        short = lambda ref: ref.split(".")[-1]
        have = [e for e in p["members"]
                if short(e) in p["persist"] and not p["extra"][short(e)]]
        rest = [short(e) for e in p["members"]
                if short(e) not in p["persist"] or p["extra"][short(e)]]
        path = (d / p["file"]).resolve()
        s = path.read_text()

        # 1. alternation, at context scope just before the repository
        rm = re.search(rf"^( *)repository {R} (?:as \w+ )?is \{{", s, re.M)
        if not rm:
            print(f"  SKIP {R}: cannot locate its declaration")
            continue
        ind = rm.group(1)
        if f"type {R}Command is one of" not in s:
            alt = (f"{ind}type {R}Command is one of {{\n{ind}  "
                   + " or ".join(f"{ctx}.{R}.Persist{short(e)}" for e in have)
                   + f"\n{ind}}} with {{\n{ind}  briefly \"Anything that writes the {R}\"\n"
                     f"{ind}  described as {{\n"
                     f"{ind}    |The persistence commands {R} accepts. Entity events never reach\n"
                     f"{ind}    |it directly; {proj} turns each into one of these. A repository\n"
                     f"{ind}    |takes commands and queries only.\n{ind}  }}\n{ind}}}\n")
            s = s[:rm.start()] + alt + s[rm.start():]

        # 2. the event inlet becomes a command inlet
        old_inlet = re.search(rf"( *)inlet {p['inlet']['id']} is type [\w.]+", s)
        if not old_inlet:
            print(f"  SKIP {R}: cannot locate inlet {p['inlet']['id']}")
            continue
        new_inlet_id = f"{R}From{proj}"
        s = s[:old_inlet.start()] + f"{old_inlet.group(1)}inlet {new_inlet_id} is type {R}Command" + s[old_inlet.end():]

        # 3. the projector, after the repository's closing block
        rm2 = re.search(rf"^( *)repository {R} (?:as \w+ )?is \{{", s, re.M)
        i = rm2.start(); j = s.index("{", i); dep, k = 1, j + 1
        while dep and k < len(s):
            dep += (s[k] == "{") - (s[k] == "}"); k += 1
        t = re.match(r"[ \t]*with[ \t]*\{", s[k:])
        if t:
            a = k + t.end() - 1; dep, k2 = 1, a + 1
            while dep and k2 < len(s):
                dep += (s[k2] == "{") - (s[k2] == "}"); k2 += 1
            k = k2
        k = s.index("\n", k) + 1
        clauses = "".join(
            f"{ind}    on {low(short(e))}: event {e} is {{\n"
            f"{ind}      tell command {ctx}.{R}.Persist{short(e)}("
            f"{p['idf'][short(e)]} = {low(short(e))}.{p['srcf'][short(e)]}) to repository {ctx}.{R}\n"
            f"{ind}    }}\n" for e in have)
        if rest:
            clauses += (f"{ind}    on other is {{\n"
                        f'{ind}      do "not persisted: {", ".join(rest[:4])}'
                        + (f" and {len(rest)-4} more" if len(rest) > 4 else "")
                        + f' record no stored state"\n{ind}    }}\n')
        block = (f"{ind}projector {proj} as flow is {{\n"
                 f"{ind}  updates repository {ctx}.{R}\n"
                 f"{ind}  inlet {proj}From{ent} is type {p['inlet']['type']['ref']}\n"
                 f"{ind}  outlet {proj}ToRepository is type {R}Command\n"
                 f"{ind}  handler {proj}Handler is {{\n{clauses}{ind}  }} with {{\n"
                 f"{ind}    briefly \"{proj} handler\"\n{ind}    described as {{\n"
                 f"{ind}      |Turns each {ent} event into the repository command that writes it.\n"
                 f"{ind}    }}\n{ind}  }}\n{ind}}} with {{\n"
                 f"{ind}  briefly \"{ent} persistence projection\"\n{ind}  described as {{\n"
                 f"{ind}    |Builds the stored {ent} view from the entity's events.\n"
                 f"{ind}  }}\n{ind}}}\n")
        s = s[:k] + block + s[k:]

        # 4. repoint the feeding connector, and add the storage leg
        old_to = p["conn"]["to"]["ref"]
        cm = re.search(rf"(connector\s+(?:'[^']*'|\w+)\s+is\s+from\s+outlet\s+[\w.]+\s+to\s+inlet\s+){re.escape(old_to)}", s)
        if not cm:
            print(f"  SKIP {R}: cannot locate the feeding connector to {old_to}")
            continue
        s = s[:cm.start()] + cm.group(1) + f"{ctx}.{proj}.{proj}From{ent}" + s[cm.end():]
        cm2 = re.search(rf"^( *)connector\s", s, re.M)
        s = (s[:cm2.start()]
             + f"{cm2.group(1)}connector '{proj} Storage' is from outlet {ctx}.{proj}.{proj}ToRepository "
               f"to inlet {ctx}.{R}.{new_inlet_id} with {{\n"
               f'{cm2.group(1)}  briefly "{proj} commands on their way to {R}"\n'
               f"{cm2.group(1)}}}\n" + s[cm2.start():])
        if not dry:
            path.write_text(s)
        print(f"  {R}: {len(have)} persisted, {len(rest)} via on other -> {proj}")


if __name__ == "__main__":
    main()
