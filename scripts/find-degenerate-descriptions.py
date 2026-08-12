#!/usr/bin/env python3
"""Flag field descriptions whose words add nothing beyond the identifier.

A field is `name: Type with {` followed by briefly/described text. It is
degenerate when the description contributes no word beyond the identifier's
own (camelCase split), after discarding a STRUCTURAL-ONLY stoplist.

    ./scripts/find-degenerate-descriptions.py <dir-or-file> [--novel=N] [-v]

`--novel=N` loosens the rule to "adds at most N words"; N=0 is the figure
BACKLOG.md reports. `-v` lists each site as `file:line: ident -> description`.

THIS IS A POINTER TO CANDIDATES, NOT A SCORE. It under-reports prose that is
vague without being identical to its identifier ("Identifier for the menu
item" on `ticketMenuItemId` reads as novel because "identifier" is a word).
Counts from different versions of this script ARE NOT COMPARABLE -- three
have been used on this corpus and all three disagree; see BACKLOG.md #1.
Its calibration check is that a context already rewritten reads ~0 while a
pending one does not.

Domain nouns (amount, status, station, date) are deliberately absent from
the stoplist: stripping them would call real prose empty.
"""
import re, sys, pathlib, collections

FIELD = re.compile(r'^\s*([A-Za-z][A-Za-z0-9]*)\s*:\s*[^\n]*?\bwith\s*\{\s*$')
BRIEF = re.compile(r'^\s*briefly\s+"([^"]*)"')
PIPE  = re.compile(r'^\s*\|(.*)$')

# Words that carry no domain intent: articles, copulas, and the vocabulary of
# restating a field ("unique identifier for the X", "whether X has been set").
FILLER = {
    'the','a','an','of','for','to','in','is','are','this','that','with','and',
    'its','it','be','been','has','have','had','was','were','on','at','by','or',
    'if','as','from','when','which','whether','any','all','each','no','not',
    # Structural only. Domain nouns (amount, status, date, station, table…)
    # are deliberately NOT here — stripping them would call real prose empty.
    'unique','identifier','optional','associated','related','being','s',
    'indicates','indicating','represents','representing','denotes','denoting',
    'specifies','specifying','holds','holding','contains','containing',
}

def words(s):
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', s)
    return {w for w in re.findall(r'[a-z0-9]+', s.lower()) if w not in FILLER}

def scan(path):
    lines = path.read_text().splitlines()
    hits = []
    for i, line in enumerate(lines):
        m = FIELD.match(line)
        if not m:
            continue
        ident = m.group(1)
        desc, depth, j = [], 1, i + 1
        while j < len(lines) and depth > 0:
            depth += lines[j].count('{') - lines[j].count('}')
            if depth <= 0:
                break
            b = BRIEF.match(lines[j])
            p = PIPE.match(lines[j])
            if b: desc.append(b.group(1))
            if p: desc.append(p.group(1))
            j += 1
        if not desc:
            hits.append((i + 1, ident, '<none>'))
        else:
            novel = words(' '.join(desc)) - words(ident)
            if len(novel) <= NOVEL:
                hits.append((i + 1, ident, ' / '.join(desc).strip()))
    return hits

NOVEL = int(([a.split('=')[1] for a in sys.argv if a.startswith('--novel=')] or ['0'])[0])
args=[a for a in sys.argv[1:] if not a.startswith('-')]
root = pathlib.Path(args[0] if args else '.')
total, byfile = 0, collections.Counter()
targets = [root] if root.is_file() else sorted(root.rglob('*.riddl'))
for f in targets:
    for ln, ident, d in scan(f):
        total += 1
        byfile[str(f)] += 1
        if '-v' in sys.argv:
            print(f'{f}:{ln}: {ident}  ->  {d}')
for f, n in byfile.most_common():
    print(f'{n:5d}  {f}')
print(f'{total:5d}  TOTAL')
