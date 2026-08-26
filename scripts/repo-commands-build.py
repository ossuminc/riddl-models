#!/usr/bin/env python3
"""Second half of "repositories take COMMANDS", driven by riddlc's own output.

Run AFTER scripts/repo-commands.py has stripped the event inlets and dead
scaffolding. This reads `riddlc validate` for the model and acts on what it
actually says -- the findings name every alternation member that needs a
clause, and the ascription errors name the shape each processor must carry.

It re-validates after each phase, so every step acts on current truth rather
than on a stale plan. A model is finished when riddlc reports nothing at any
severity; anything this cannot resolve is left for hand work and reported.

Usage:  ./scripts/repo-commands-build.py <model-dir>
"""
import re
import subprocess
import sys
from pathlib import Path

RIDDLC = "/Users/reid/Code/ossuminc/bin/riddlc"
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def lower1(s):
    return s[0].lower() + s[1:]


class M:
    def __init__(self, d):
        self.d = Path(d)
        conf = sorted(self.d.glob("*.conf"))
        m = re.search(r'input-file\s*=\s*"?([^"\s]+)"?', conf[0].read_text()) if conf else None
        self.entry = m.group(1) if m else f"{self.d.name}.riddl"
        self.load()

    def load(self):
        self.t = {p: p.read_text() for p in sorted(self.d.glob("*.riddl"))}

    def save(self):
        for p, s in self.t.items():
            p.write_text(s)

    def validate(self):
        r = subprocess.run([RIDDLC, "--no-ansi-messages", "validate", self.entry],
                           cwd=self.d, capture_output=True, text=True)
        return ANSI.sub("", r.stdout + "\n" + r.stderr)

    def findings(self):
        out, cur = [], None
        for ln in self.validate().split("\n"):
            m = re.match(r"^\[(\w+)\]\s*(?:\[[\w-]+\]\s*)?([\w.]+\.riddl)\((\d+):", ln)
            if m:
                cur = {"sev": m.group(1), "file": m.group(2), "line": int(m.group(3)), "msg": ""}
                out.append(cur)
            elif cur is not None and ln.strip() and not cur["msg"]:
                cur["msg"] = ln.strip()
        return out

    def all(self):
        return "\n".join(self.t.values())

    def find(self, pat, flags=0):
        for p, s in self.t.items():
            m = re.search(pat, s, flags)
            if m:
                return p, m
        return None, None

    def alt_members(self, name):
        p, m = self.find(rf"\btype\s+{name.split('.')[-1]}\s+is\s+one\s+of\s*\{{(.*?)\}}", re.S)
        if not m:
            return None
        return [x.split(".")[-1] for x in re.split(r"\s+or\s+", m.group(1).strip()) if x.strip()]

    def event_owner_and_id(self, ev):
        """(owning entity or None, id field, id type) for an event."""
        for p, s in self.t.items():
            m = re.search(rf"\bevent\s+{ev}\s+is\s*\{{", s)
            if not m:
                continue
            i = s.index("{", m.start())
            depth, j = 1, i + 1
            while depth and j < len(s):
                depth += (s[j] == "{") - (s[j] == "}")
                j += 1
            f = re.search(r"^\s*(\w+)\s*:\s*([\w.]+(?:\([^)]*\))?)", s[i + 1:j - 1], re.M)
            owner = None
            for em in re.finditer(r"\bentity\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{", s):
                k = s.index("{", em.start())
                dd, jj = 1, k + 1
                while dd and jj < len(s):
                    dd += (s[jj] == "{") - (s[jj] == "}")
                    jj += 1
                if k < m.start() < jj:
                    owner = em.group(1)
            if f:
                return owner, f.group(1), f.group(2)
        return None, None, None


def phase_projectors(mm):
    """One `on event` clause per unhandled alternation member, telling the
    matching Persist command. riddlc REJECTS `send` to an outlet here: a
    projector must TELL a repository to count as persisting its projection."""
    fs = [f for f in mm.findings()
          if "admits Type" in f["msg"] and "Projector" in f["msg"]]
    if not fs:
        return 0
    repo, _ = mm.find(r"\brepository\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{")
    rm = re.search(r"\brepository\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{", mm.all())
    if not rm:
        return 0
    repo_name = rm.group(1)
    rp, rmatch = mm.find(rf"[ \t]*repository\s+{repo_name}\s+(?:as\s+\w+\s+)?is\s*\{{")
    ctx = re.search(r"\bcontext\s+([A-Z]\w*)\s", mm.all())
    repo_path = f"{ctx.group(1)}.{repo_name}" if ctx else repo_name

    need, plans = {}, {}
    for f in fs:
        g = re.search(r"Projector '([\w.]+)'.*?members \(([^)]*)\)", f["msg"])
        if not g:
            continue
        proj = g.group(1).split(".")[-1]
        for ev in [x.strip() for x in g.group(2).split(",") if x.strip()]:
            owner, fld, typ = mm.event_owner_and_id(ev)
            if not fld:
                continue
            need[ev] = (owner, fld, typ)
            plans.setdefault(proj, []).append(ev)
    if not need:
        return 0

    have = set(re.findall(r"command (Persist\w+) is", mm.all()))
    todo = [e for e in need if f"Persist{e}" not in have]

    decls = "".join(
        f"    command Persist{e} is  {{\n      {need[e][1]}: {need[e][2]} with {{\n"
        f'        briefly "Row addressed"\n        described as {{\n'
        f"          |Which stored row {e} applies to.\n        }}\n      }}\n"
        f'    }} with {{\n      briefly "Persist {e}"\n      described as {{\n'
        f"        |Instructs this repository to apply {e} to the stored row. A\n"
        f"        |persistence command, not a domain command: it declares no `yields`\n"
        f"        |because storing a row records no new entity state.\n      }}\n    }}\n"
        for e in todo)
    onc = "".join(
        f"      on persist{e}: command Persist{e} is {{\n"
        f'        do "apply {e} to the stored row"\n      }}\n' for e in todo)

    s = mm.t[rp]
    ins = []
    for proj, evs in plans.items():
        pp, pm = mm.find(rf"[ \t]*projector\s+{proj}\s+(?:as\s+\w+\s+)?is\s*\{{")
        if not pm:
            continue
        gen = ""
        for e in evs:
            owner, fld, _ = need[e]
            q = f"{owner}.{e}" if owner else e
            b = lower1(e)
            gen += (f"      on {b}: event {q} is {{\n"
                    f"        tell command {repo_path}.Persist{e}({fld} = {b}.{fld})"
                    f" to repository {repo_path}\n"
                    f'        do "apply {e} to the {proj} projection"\n      }}\n')
        ps = mm.t[pp]
        hm = re.search(r"[ \t]*handler \w+ is \{", ps[pm.start():])
        if not hm:
            continue
        at = pm.start() + hm.end()
        mm.t[pp] = ps[:at] + "\n" + gen.rstrip("\n") + ps[at:]

    s = mm.t[rp]
    rmatch = re.search(rf"[ \t]*repository\s+{repo_name}\s+(?:as\s+\w+\s+)?is\s*\{{", s)
    hm = re.search(r"[ \t]*handler \w+ is \{", s[rmatch.start():])
    ins = []
    if hm and onc:
        ins.append((rmatch.start() + hm.end(), "\n" + onc.rstrip("\n")))
    if decls:
        ins.append((s.index("{", rmatch.start()) + 1, "\n" + decls.rstrip("\n")))
    for at, txt in sorted(ins, key=lambda x: -x[0]):
        s = s[:at] + txt + s[at:]
    mm.t[rp] = s
    mm.save()
    return len(todo)


def phase_yields(mm):
    """Entity self-tell -> `yield event`, plus an `on event` clause to receive
    it, plus `yields` on the command. Declaring `yields` obliges EVERY handler
    of that command, so relays must switch to `forward` (phase_forward)."""
    n = 0
    for p, s in list(mm.t.items()):
        for em in list(re.finditer(r"\bentity\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{", s)):
            ent = em.group(1)
            evs = []

            def rep(m):
                evs.append(m.group(1))
                return f"yield event {m.group(1)}({m.group(2)})"
            s2 = re.sub(rf"tell event (\w+)\((.*?)\) to entity {ent}(?![\w.])", rep, s)
            if not evs:
                continue
            s = s2
            n += len(evs)
            for m in re.finditer(r"on (\w+): command (\w+) is \{((?:[^{}]|\{[^{}]*\})*)\}", s):
                y = re.search(r"yield event (\w+)\(", m.group(3))
                if y:
                    s = re.sub(rf"(\n  command {m.group(2)})(?! yields) is",
                               rf"\1 yields event {y.group(1)} is", s, count=1)
            hm = re.search(rf"[ \t]*handler {ent}Handler is \{{", s)
            if hm:
                gen = "".join(
                    f"    on {lower1(e)}: event {e} is {{\n"
                    f'      do "apply {e} to the {ent.lower()} so it can be persisted'
                    f' and replayed"\n    }}\n' for e in sorted(set(evs)))
                s = s[:hm.end()] + "\n" + gen.rstrip("\n") + s[hm.end():]
            mm.t[p] = s
    mm.save()
    return n


def phase_forward(mm):
    """A command that declares `yields` obliges every handler. A relay that
    only passes it on uses `forward`, which discharges the obligation."""
    src = mm.all()
    changed = 0
    for p, s in list(mm.t.items()):
        for hm in list(re.finditer(r"handler \w+ is \{", s)):
            pass
        def fix(m):
            nonlocal changed
            cmd = m.group(2).split(".")[-1]
            if re.search(rf"command {cmd} yields event", src):
                changed += 1
                return m.group(0).replace("send ", "forward ", 1)
            return m.group(0)
        s = re.sub(r"(on \w+: command ([\w.]+) is \{\n[ \t]*)send \w+ to outlet [\w.]+",
                   lambda m: fix(m), s)
        mm.t[p] = s
    mm.save()
    return changed


def phase_entity_commands(mm):
    """An entity inlet admits its command alternation; every member needs a
    clause. Mostly `Initialize<X>`, which nothing ever handled."""
    n = 0
    for f in mm.findings():
        g = re.search(r"but Entity '([\w.]+)' declares no handler clause for "
                      r"\d+ of its \d+ members \(([^)]*)\)", f["msg"])
        if not g:
            continue
        ent = g.group(1).split(".")[-1]
        members = [x.strip() for x in g.group(2).split(",") if x.strip()]
        hp, hm = mm.find(rf"[ \t]*handler {ent}Handler is \{{")
        if not hm:
            ep, em = mm.find(rf"[ \t]*entity\s+{ent}\s+(?:as\s+\w+\s+)?is\s*\{{")
            if not em:
                continue
            hp = ep
            hm = re.search(r"[ \t]*handler \w+ is \{", mm.t[ep][em.start():])
            if not hm:
                continue
            at = em.start() + hm.end()
        else:
            at = hm.end()
        gen = "".join(
            f"    on {lower1(c)}: command {c} is {{\n"
            f'      do "apply {c} to the {ent.lower()}"\n    }}\n' for c in members)
        s2 = mm.t[hp]
        mm.t[hp] = s2[:at] + "\n" + gen.rstrip("\n") + s2[at:]
        n += len(members)
        mm.save()
        mm.load()
    return n


def phase_drop_degenerate(mm):
    """`Initialize<X>` commands have body `???`, are sent by nothing and were
    handled by nothing. They are placeholders, not modelled commands, so they
    are deleted rather than given an invented event to emit. This is not the
    inlet prohibition -- no inlet is removed, only a vestigial command."""
    n = 0
    src = mm.all()
    for cmd in sorted(set(re.findall(r"command (Initialize\w+) is\s*\{ \?\?\? \}", src))):
        uses = len(re.findall(rf"\b{cmd}\b", src))
        # a relay sends the BINDER, not the command name, so a name search is
        # not evidence of use; only a construction `Cmd(...)` is.
        if re.search(rf"\b{cmd}\s*\(", src):
            continue
        for p_, s_ in list(mm.t.items()):
            s2 = re.sub(rf"[ \t]*command {cmd} is\s*\{{ \?\?\? \}}[ \t]*with\s*\{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}}\n", "", s_)
            s2 = re.sub(rf"[ \t]*on \w+: command [\w.]*{cmd} is \{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}}\n", "", s2)
            s2 = re.sub(rf"[ \t]*on command [\w.]*{cmd} is \{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}}\n", "", s2)
            s2 = re.sub(rf"\s+or\s+[\w.]*\.?{cmd}\b", "", s2)
            s2 = re.sub(rf"\b[\w.]*\.?{cmd}\s+or\s+", "", s2)
            if s2 != s_:
                mm.t[p_] = s2
                n += 1
        mm.save()
        mm.load()
    return n


def phase_reachability(mm):
    """A `tell` does not make a repository reachable -- a connector to one of
    its inlets does. The repository takes COMMANDS, so the inlet is typed by an
    alternation of its own Persist commands, fed from the projector."""
    src = mm.all()
    if not any("not reachable via any connector" in f["msg"] for f in mm.findings()):
        return 0
    rm = re.search(r"\brepository\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{", src)
    ctx = re.search(r"\bcontext\s+([A-Z]\w*)\s", src)
    if not rm or not ctx:
        return 0
    repo, ctxn = rm.group(1), ctx.group(1)
    alt = f"{repo}Command"
    persists = sorted(set(re.findall(r"command (Persist\w+) is", src)))
    if not persists:
        return 0
    rp, rmatch = mm.find(rf"[ \t]*repository\s+{repo}\s+(?:as\s+\w+\s+)?is\s*\{{")
    pp, pmatch = mm.find(r"[ \t]*projector\s+([A-Z]\w*)\s+(?:as\s+\w+\s+)?is\s*\{")
    if not rmatch or not pmatch:
        return 0
    proj = re.search(r"projector\s+([A-Z]\w*)", pmatch.group(0)).group(1)
    out = f"{proj}ToRepository"
    inlet = f"{repo}From{proj}"

    if not re.search(rf"\btype\s+{alt}\s+is\s+one\s+of", src):
        decl = (f"  type {alt} is one of {{\n    "
                + " or ".join(f"{ctxn}.{repo}.{c}" for c in persists)
                + f"\n  }} with {{\n    briefly \"Anything that writes {repo}\"\n"
                  f"    described as {{\n"
                  f"      |The persistence commands {repo} accepts. Entity events never\n"
                  f"      |reach it directly; a projector turns each into one of these.\n"
                  f"    }}\n  }}\n")
    else:
        decl = ""

    s = mm.t[pp]
    pmatch = re.search(r"[ \t]*projector\s+" + proj + r"\s+(?:as\s+\w+\s+)?is\s*\{", s)
    at = s.index("{", pmatch.start()) + 1
    mm.t[pp] = s[:at] + f"\n    outlet {out} is type {alt}" + s[at:]

    s = mm.t[rp]
    rmatch = re.search(rf"[ \t]*repository\s+{repo}\s+(?:as\s+\w+\s+)?is\s*\{{", s)
    ins = [(s.index("{", rmatch.start()) + 1, f"\n    inlet {inlet} is type {alt}")]
    if decl:
        ins.append((s.rfind("\n", 0, rmatch.start()) + 1, decl))
    conn = (f"  connector '{proj} Storage' is from outlet {ctxn}.{proj}.{out}"
            f" to inlet {ctxn}.{repo}.{inlet} with {{\n"
            f"    briefly \"{proj} updates on their way to storage\"\n  }}\n")
    tail = s.rindex("\n} with {") + 1 if "\n} with {" in s else s.rindex("\n}") + 1
    ins.append((tail, conn))
    for a, t in sorted(ins, key=lambda x: -x[0]):
        s = s[:a] + t + s[a:]
    mm.t[rp] = s
    mm.save()
    return 1


def phase_ascriptions(mm):
    """riddlc names the correct shape in its own error text. Never derive it."""
    fixed = 0
    for f in mm.findings():
        g = re.search(r"'([\w.]+)' is ascribed 'as (\w+)' but its DATAFLOW arity "
                      r"\([^)]*\) is (\w+)", f["msg"])
        if not g:
            continue
        name, was, want = g.group(1).split(".")[-1], g.group(2), g.group(3)
        for p, s in list(mm.t.items()):
            new = re.sub(rf"((?:processor|repository|projector|entity|context)\s+{name})\s+as\s+{was}\s+is",
                         rf"\1 as {want} is", s, count=1)
            if new != s:
                mm.t[p] = new
                fixed += 1
                break
    mm.save()
    return fixed


def main():
    mm = M(sys.argv[1])
    a = phase_projectors(mm); mm.load()
    b = phase_yields(mm);     mm.load()
    c = phase_forward(mm);    mm.load()
    phase_reachability(mm);   mm.load()
    phase_entity_commands(mm); mm.load()
    phase_drop_degenerate(mm); mm.load()
    d = 0
    for _ in range(4):
        n = phase_ascriptions(mm)
        mm.load()
        d += n
        if not n:
            break
    fs = mm.findings()
    print(f"{mm.d}: persists+{a} yields+{b} forwards+{c} ascriptions+{d} "
          f"-> {len(fs)} findings, {sum(1 for f in fs if f['sev']=='error')} errors")
    for f in fs[:6]:
        print(f"    [{f['sev']}] {f['file']}:{f['line']} {f['msg'][:96]}")


if __name__ == "__main__":
    main()
