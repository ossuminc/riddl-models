#!/usr/bin/env python3
"""A3 + B3 `with history`: the `Log<X>Event` repository handlers said "append
the event to the <X> event log" and no schema declared an event-log table, so
a generator's fill had to invent one. Declare it: a `Logged<X>Event` record, an
`of <x>Events as record Logged<X>Event with history` entry, and a `store` in
place of the prose.

    ./scripts/event-log-tables.py <model-dir>
"""
import re,sys
from pathlib import Path
D=Path(sys.argv[1]).resolve()
def lc(s): return s[0].lower()+s[1:]
def block(s,i):
    depth=0; j=s.index("{",i)
    while j<len(s):
        if s[j]=="{": depth+=1
        elif s[j]=="}":
            depth-=1
            if depth==0: return j
        j+=1
    return len(s)
n=0
for f in sorted(D.rglob("*.riddl")):
    t=f.read_text(); orig=t
    while True:
        m=re.search(r"\n( +)on command (Log(\w+)Event) is \{\n +do \"append [^\"]*\"\n +\}",t)
        if not m: break
        ind,cmd,base=m.groups()
        # the command's fields
        cm=re.search(r"\n( +)command "+cmd+r" is \{",t)
        if not cm: print("  no command",cmd); break
        cb=t[cm.start():block(t,cm.start())+1]
        fs=re.findall(r"\n {4}(\w+): ([^\n]+?) with \{",cb)
        if len(fs)<2: print("  command",cmd,"has",len(fs),"fields"); break
        # the schema in the same repository
        sm=None
        for cand in re.finditer(r"\n( +)schema (\w+) is relational\n((?: +of \w+ as record [\w.]+\n| +(?:key|index) on field [\w.]+\n)+)",t):
            if cand.start()<m.start(): sm=cand
        if not sm: print("  no schema before",cmd); break
        sind,sname,body=sm.groups()
        ofs=[l for l in body.split("\n") if " of " in l]
        rest=[l for l in body.split("\n") if l.strip() and " of " not in l]
        rec=f"Logged{base}Event"
        # 1. the record, beside the command
        decl=(f'\n{cm.group(1)}record {rec} is {{\n'
              +"".join(f'{cm.group(1)}  {a}: {b} with {{\n{cm.group(1)}    briefly "{a[0].upper()+a[1:]}"\n'
                       f'{cm.group(1)}    described as {{\n{cm.group(1)}      |As the logged event carried it.\n'
                       f'{cm.group(1)}    }}\n{cm.group(1)}  }}\n' for a,b in fs)
              +f'{cm.group(1)}  loggedAt: TimeStamp with {{\n{cm.group(1)}    briefly "Logged at"\n'
              f'{cm.group(1)}    described as {{\n{cm.group(1)}      |When the log row was written.\n'
              f'{cm.group(1)}    }}\n{cm.group(1)}  }}\n'
              f'{cm.group(1)}}} with {{\n{cm.group(1)}  briefly "A logged {base} event"\n'
              f'{cm.group(1)}  described as {{\n{cm.group(1)}    |One row of the {base} event log: which {base.lower()}, which event,\n'
              f'{cm.group(1)}    |and when it was recorded. `with history` on the entry keeps every\n'
              f'{cm.group(1)}    |version, which is what a log is.\n'
              f'{cm.group(1)}  }}\n{cm.group(1)}}}')
        table=lc(base)+"Events"
        newbody="\n".join(ofs+[f"{sind}  of {table} as record {rec} with history"]+rest)+"\n"
        b_=lc(cmd)
        newclause=(f'\n{ind}on {b_}: command {cmd} is {{\n'
                   f'{ind}  store record {rec}('
                   +", ".join(f"{a} = {b_}.{a}" for a,_ in fs)
                   +f', loggedAt = system.now) in {sname}.{table}\n{ind}}}')
        t=t[:m.start()]+newclause+t[m.end():]
        # re-find the schema (offsets moved) and the command
        sm2=re.search(r"\n( +)schema "+sname+r" is relational\n((?: +of \w+ as record [\w.]+(?: with history)?\n| +(?:key|index) on field [\w.]+\n)+)",t)
        t=t[:sm2.start(2)]+newbody+t[sm2.end(2):]
        cm2=re.search(r"\n( +)command "+cmd+r" is \{",t)
        t=t[:cm2.start()]+decl+t[cm2.start():]
        n+=1
    if t!=orig: f.write_text(t)
print(f"{n} event-log tables declared")
