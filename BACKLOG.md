# BACKLOG.md — riddl-models

Open work. Completed items leave: lessons to NOTEBOOK.md, durable facts to
CLAUDE.md. Verified claims carry their evidence so nothing is re-derived.

---

## 1. Make reactive-bbq the reference model (ACTIVE CAMPAIGN)

The plan is `~/.claude/plans/wobbly-whistling-finch.md`, approved
2026-08-12, with five scoping decisions taken the same day. The rules it is
measured against are `docs/SIMULABILITY-AND-GENERATABILITY.md`, and
`ReactiveBbqCompletenessTest` enforces them. **That suite is red on purpose
— 3 of 10 rules pass — so `sbt checkAll` exits 1 until this campaign
finishes. That is expected, not a breakage.**

### Where it stopped

**Phase 0 (rules + harness) and part of Phase 1 are done.** **FrontOfHouse
and Kitchen** have had their descriptions rewritten and both read 0. Next
context is **Bar**, then Loyalty, OnlineOrdering, Delivery, then backoffice
and corporate.

Measured at rc.13 on 2026-08-12, by running it:

| item | state |
|---|---|
| reactive-bbq warnings | **18**, all `X populates Repository R but is not defined in it` (10 event, 8 command) |
| degenerate descriptions left | **324** — restaurant 146, corporate 107, backoffice 71 |
| `???` bodies | 20 (13 `Initialize<Entity>`, 7 `on init`) |
| terms | 2 (rule wants >= 20) |
| groups / `put` / `version` | 1 / 0 / 0 |
| epic interaction blocks | no sequential/parallel/optional |

#### The degenerate-description count is DETECTOR-RELATIVE

Three detectors have now been used and they disagree; **no two of their
numbers may be compared**, and none of them is "the" count:

| detector | reactive-bbq total | rule |
|---|---:|---|
| pre-2026-08-12, wide | 247 (`restaurant/` alone) | also matched definition lines |
| 2026-08-12, fields-only | 259 | description words ⊆ identifier words |
| 2026-08-13, fields-only | **324** | same, plus a small structural stoplist |

The current one is **`scripts/find-degenerate-descriptions.py`**, committed
on 2026-08-13. The earlier decision not to keep it is reversed: three
throwaway detectors produced three incomparable numbers, and re-deriving it
each session is exactly what made the figures untrustworthy.

```bash
./scripts/find-degenerate-descriptions.py hospitality/food-service/reactive-bbq
./scripts/find-degenerate-descriptions.py <path> --novel=0 -v   # list sites
```

It flags a field (`name: Type with {`) whose description contributes no word
beyond the identifier's, after discarding a **structural-only** stoplist
(`unique`, `identifier`, `optional`, `indicates`, …). Domain nouns are
deliberately NOT in that stoplist: stripping `amount`, `status` or `station`
would call real prose empty. `--novel=N` loosens it to "adds at most N
words"; `N=0` is the reported figure.

**It is a pointer to candidates, not a score.** It under-reports
vague-but-not-identical prose in both directions, and its calibration check
is that an already-rewritten context reads ~0 while a pending one does not.

**A "0 remaining" claim means "0 under the detector then in use."** On
2026-08-13 the stricter detector found **8** sites in FrontOfHouse that the
2026-08-12 run had reported as 0 — not a regression, and not a false claim
at the time. Re-run the current detector over contexts already marked done
before trusting them.

### The five scoping decisions

1. **Round-trip is hygiene, not a criterion.** BAST is a performance
   optimisation for getting an AST into memory. The pipeline is text ->
   validate with zero messages -> AST -> run, and **AST quality is the
   whole game**.
2. **Every degenerate description gets real domain intent** — invent it, it
   is a restaurant. This is the largest item and the most important for
   generatability: the deterministic generator emits `[[AI FILL: ...]]` and
   the AI tier fills it from surrounding context, so a description that
   restates its identifier IS the absence of context.
3. **Coverage is once-each.** Statements and definitions matter far more
   than exhaustive type expressions; use type expressions as the domain
   warrants.
4. **Canonical only, pinned by the test. Zero deprecation warnings.**
5. **Let it grow**, splitting by MAJOR definition: one context per file, a
   large entity in its own file, never a definition split across files, new
   application contexts each in their own file.

### Phases remaining

- **1** — 18 populates-repository warnings; 20 `???`; the 259 descriptions
- **2** — saga, correlation (A70), invariant/require, function/return,
  constant, foreach, become, `void` streamlet, a healthy mix of type
  expressions
- **3** — companion `language-coverage/` model for what a restaurant cannot
  justify (module, bast_import, replica, graph/table, nebula, method,
  attachment/ULID, `described at`/`in file`)
- **4** — UI per domain (groups, inputs, outputs, `put`) and every epic
  interaction step kind
- **5** — the corpus-wide populates-repository campaign, ~855 sites in the
  other 186 models
- **6** — upstream task for riddlc: a run-ending fitness summary, plus the
  cycle check below

### One rule with no check behind it

**A cycle in the connector graph has no detection in riddlc** (verified
2026-08-12: no cycle/circular/acyclic logic in
`StreamingValidation.scala`), and it is precisely the model a discrete-event
simulator cannot finish. Unconnected ports ARE checked (`:203`, `:583`).
This belongs in the Phase 6 upstream task.

## 2. Pattern templates: 2 of 7 validate as whole models

`scripts/verify-templates.py` gates on **parse**, and all 7 pass. Under
`--validate` only 2 do (`repository`, `read-model`).

The remaining findings split two ways, and only the first is actionable:

- **Real**: entity templates have no `on query` clause, so nothing can read
  them. Worth adding.
- **Inherent to being a fragment**: "declare the Id type in the containing
  context" is impossible when the template *is* the entity, and a template
  cannot connect its own outlet.

Decide whether `--validate` should ever become a gate, or stay advisory.
Findings naming a scaffold definition are already classified out, so what
`--validate` reports is genuinely about the template.

## 3. Pattern examples diverge from canonical formatting (deliberate)

`patterns/entity/*/example.riddl` differ from `riddlc prettify` output by
**151 lines** — hand-wrapped alternations, `Decimal(12, 2)` spacing. They
are documentation, and canonicalising would emit 341-character alternations
and two ports per line.

They are excluded from `scripts/verify-bast-roundtrip.sh` for that reason;
their `.bast` are still regenerated. Revisit if prettify's port/alternation
formatting improves — riddl has recorded that **formatting waits for the 2.0
release** (`fdc5c1718`).

## 4. `main` stays on 1.x until riddl 2.0 ships

`origin/main` is **72 commits behind** `release/2` and still carries
`state X of type Y`. Reid's decision, 2026-08-04: leave it. `release/2` pins
a staged, unpublished RC, so merging would make the default branch depend on
something nobody can resolve.

Synapify reads `release/2` and has a settings panel for it. **Merge when
riddl 2.0 ships**, not before. Full reasoning in
`task/done/main-still-1x-syntax-breaks-consumers.md`.

## 5. `sbt test` is a weak gate for model edits

sbt 2 routes `test` to `testQuick`, which skips tests it believes unchanged,
and the suite reads `.riddl` files at **run** time — so sbt never sees a
model edit as an input. A second `sbt test` reports success having run
nothing.

**`sbt checkAll` is the command to trust, and as of 2026-08-12 it can
actually fail.** It could not before: the alias ran `Test/executeTests`,
which RUNS everything but yields its outcome as a VALUE, so sbt exited 0
with seven failing assertions. `checkTests` in `build.sbt` now inspects
`result.overall` and calls `sys.error`, and logs the suite count so a run
that measured almost nothing is visible rather than merely green. Verified
both directions.

Could still be improved by declaring the model files as task inputs so sbt
invalidates properly.

## 6. No CI in this repository

`.github/` contains only `FUNDING.yml`. Every gate runs locally.

riddl's own CI validates this corpus externally via
`validate_external_riddl.py`, but that will not catch template rot — the
templates are not parseable models.

A workflow running `sbt checkAll` on push needs the pinned riddlc to be
resolvable, so it is blocked until riddl 2.0 publishes (or the workflow
builds riddl from source).

## 7. Watch: staged binary swaps invalidate `.bast` silently

On 2026-08-04 the `.bast` committed at 21:11 were stale by 22:27 with no
source change — because `../bin/riddlc` was restaged underneath. Bastify is
deterministic (two consecutive runs produce identical bytes; verified by
`md5`), so a `.bast` diff with clean `.riddl` means **the binary moved**,
not that anything is wrong with the models.

After any restage: regenerate `.bast`, re-run the round trip, commit.

**2026-08-05 — the writer was `../riddl`, not anything here.** Mid session,
181 `.bast` were rewritten (10:09:04–07) from a tree that was clean at session
start. Each differed from `HEAD` by **9 bytes in the container only** — the
length field at `0x14` and the checksum at `0x18`; unbastifying both recovered
**byte-identical** source.

The cause was riddl's `RiddlModelsRoundTripTest` (modified in the `../riddl`
checkout), run there against this corpus and writing `.bast` from riddl's
working-tree build. Four local candidates were tested first and none
reproduced it — not `riddlcValidate`, not `Test/executeTests` at either pin,
not a `build.sbt` touch, and no file watcher exists — because **the writer
was never in this repository**. `../bin/riddlc` had not moved (`md5`
`38b557b3838d…` identical before and after).

So: an unexplained `.bast` diff means look at `../riddl` first. And note the
corollary — the corpus can be rewritten by a build you are not running, so a
diff that appears mid-session is not necessarily yours.

**The decisive check, which costs one command:** regenerate everything and ask
git.

```
./scripts/verify-bast-roundtrip.sh   # bastifies in place, then round-trips
git status --short -- '*.bast'       # empty => committed .bast are correct
```

It came back 187/187 with **zero** `.bast` modified, which proves the
committed bytes are exactly what the staged binary produces. That makes the
rule stronger than this item's original form: a `.bast` diff is only meaningful
if it **survives** a regenerate-and-compare. Restore with
`git checkout -- '*.bast'` (never delete them) and re-run that check before
believing a diff.
