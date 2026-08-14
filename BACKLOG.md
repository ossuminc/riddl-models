# BACKLOG.md — riddl-models

Open work. Completed items leave: lessons to NOTEBOOK.md, durable facts to
CLAUDE.md. Verified claims carry their evidence so nothing is re-derived.

---

## 1. Make reactive-bbq the reference model (ACTIVE CAMPAIGN)

The plan is `~/.claude/plans/wobbly-whistling-finch.md`, approved
2026-08-12, with five scoping decisions taken the same day. The rules it is
measured against are `docs/SIMULABILITY-AND-GENERATABILITY.md`, and
`ReactiveBbqCompletenessTest` enforces them. **That suite is red on purpose
— 8 of 10 rules pass — so `sbt checkAll` exits 1 until this campaign
finishes. That is expected, not a breakage.**

### Where it stopped

**Phases 0, 1, 2 and 4 are done**, and so are R3, R9, R4 and R5.
**#1b and #1c are CLOSED** — rc.14 fixed both BAST defects, the `constant`
and the interaction blocks are restored, and both survive the round trip in
the full corpus.

**Next is Phase 3**, now unblocked: `method` was fixed in the same rc.14
change as `constant`. Then Phase 5.

**The one thing standing between the campaign and 9 of 10 is not ours.**
R10 is red only because rc.14's new instance-addressing check does not
resolve `Id` type aliases (#1d). **Do not model around it** — 72 of the 86
distinct flagged messages already carry the id.

Measured at **rc.14** on 2026-08-14, every row by running the command:

| item | state |
|---|---|
| reactive-bbq errors / warnings | **0 errors**; 111 completeness messages, ALL from upstream #1d |
| degenerate descriptions left | **0** (was 358) |
| `???` bodies | **0** (was 20) |
| BAST round trip | **187/187**, 0 discrepancies, at BAST revision 16 |
| interaction blocks / `constant` | restored and surviving BAST (#1b, #1c closed) |
| terms | **25** (was 2) |
| UI groups / `put` statements | **5** (was 1) / **5** (was 0) |
| rules green | **8 of 10** — R5 green 2026-08-14; R10 red only from an upstream defect |

**The suite's 10 cases**, by their actual test names. An earlier version of
this table named the green ones "R1, R6, R7, R8, R10", which was wrong:
there are no R6/R7/R8 cases, there are **two** R5 cases, and one case
carries no rule number at all. Read from a `checkAll` run 2026-08-13:

| case | state |
|---|---|
| should exist as the reference model | green |
| R10 validate with zero errors and zero warnings | **red — upstream, see #1d** |
| R1 no `???` placeholder bodies | green |
| R2 every definition a full description, not only a brief | **red** |
| R3 domain vocabulary as terms | green **(2026-08-13)** |
| R4 UI intent with groups and `put` | green **(2026-08-13)** |
| R5 every epic interaction block kind | green **(2026-08-14)** |
| R5 every use case its own user story | green |
| R9 a version so type-delta staleness is detectable | green **(2026-08-13)** |
| R12 no deprecated spellings | green |

**What each remaining rule needs**, so the next session does not re-derive
it. These do NOT map one-to-one onto the phases:

| rule | red because | addressed by |
|---|---|---|
| R2 | **51** orphan briefs — a `briefly` with no `described` within 3 lines. All connectors and handlers: restaurant 30, corporate 11, backoffice 10 | **Reid's call: at the END of the plan**, not now |
| R10 | 111 messages from rc.14's new instance-addressing check | **NOT OURS — upstream, #1d.** Do not model around it |

**R3 and R9 are done** (2026-08-13), both unblocked by rc.14 and taken
while waiting for it:

- **R9** — one `version 1` in the `ReactiveBBQ` domain body. Reid's call:
  top-level domain only. Per A53 a definition's precise version is its
  versioned ancestors composed root-to-leaf and joined with `.`, so the
  root declaration is the leading component for everything beneath it.
  `version` is legal in `domain_content` and `processor_definition_contents`
  — verified against the grammar and probed on a scaffold before editing.
- **R3** — 2 → 25 terms. **A term goes on the definition whose own
  description uses the word** (Reid's call), not in a domain glossary, so
  most sit on *fields*. `term` is legal in any `with_metadata`, verified on
  a scaffold. The words were found by scanning every `briefly`/`described`
  line for jargon; the opaque ones were all in the low-frequency tail
  (expo, pass, par, shrinkage, stocktake, cover, check, turn, walk-in,
  no-show, void, comp, tier, tenure, earn rate, lead time, stock turn,
  courier, coverage, labor, station, prep). High-frequency words like
  `ticket` and `shift` are not jargon and were left alone.
- **Both survive BAST** — round trip 187/187, 0 discrepancies, unlike
  `constant` (#1b).

**R2 is NOT the description metric** — see the detector section below. The
358 descriptions rewritten in Phase 1 moved R2 by zero lines.

#### Two things Phase 1 turned up that were defects, not tidying

1. **218 `Persist<Event>` commands were dead.** Repositories declared them
   and had `on command` clauses for them, but `grep -c 'tell command
   Persist'` returned **0** across all 187 models. The FrontOfHouse and
   Kitchen projectors were instead telling *raw entity events* to
   repositories that have **zero `on event` clauses** — the message had no
   handler to land in. Fixed by telling the Persist command; the reference
   resolves unqualified.

2. **13 `Initialize<Entity>` commands were never handled.** Declared, named
   in an alternation, told once from a source's `on init`, and handled
   nowhere — S3 *and* S8 in `docs/SIMULABILITY-AND-GENERATABILITY.md`.
   **Removed rather than filled**: an event-sourced entity is created by its
   first real command, and each initial state already does the work with
   `on init { yield event <Creation> }`. Filling them would have invented a
   startup protocol the domain does not have.

   **A source processor's `on init` is optional** — verified by deleting one
   and revalidating to 0/0. That is what made removal possible.

#### R2 is NOT the description metric — they are disjoint

Worth knowing before sizing the rest of the plan, because it is easy to
assume the description campaign moves `ReactiveBbqCompletenessTest`. It does
not, and never could:

- **R2 measures PRESENCE** — a `briefly` with no `described` on any of the
  next 3 lines (`ReactiveBbqCompletenessTest.scala:112`). **51 orphans**,
  all of them connectors and handlers: restaurant 30, corporate 11,
  backoffice 10.
- **The degenerate-description metric measures QUALITY** — it only looks at
  *fields that already have* a description block.

Closing all 51 R2 orphans does nothing for description quality, and the 358
descriptions just rewritten moved R2 by zero lines. **Reid's call,
2026-08-13: the orphans are handled at the end of the plan**, not now.

#### The degenerate-description count is DETECTOR-RELATIVE

Three detectors have now been used and they disagree; **no two of their
numbers may be compared**, and none of them is "the" count:

| detector | reactive-bbq total | rule |
|---|---:|---|
| pre-2026-08-12, wide | 247 (`restaurant/` alone) | also matched definition lines |
| 2026-08-12, fields-only | 259 | description words ⊆ identifier words |
| 2026-08-13, fields-only | **358**, now **0** | same, plus a small structural stoplist |

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

- ~~**1** — descriptions, 18 populates-repository warnings, 20 `???`~~
  **DONE 2026-08-13.**
- ~~**2** — saga, correlation, invariant/require, function/return, foreach,
  become, `void` streamlet, type expressions~~ **DONE 2026-08-13, except
  `constant`, which is blocked upstream — see #1b.**
- **3** — companion `language-coverage/` model for what a restaurant cannot
  justify (module, bast_import, replica, graph/table, nebula, method,
  attachment/ULID, `described at`/`in file`). **UNBLOCKED at rc.14** — its
  `method` was fixed in the same change as `constant`. **Next up.**
- **4** — UI per domain (groups, inputs, outputs, `put`) and every epic
  interaction step kind. **UI half DONE 2026-08-13** — R4 green. **Epic half
  BLOCKED on rc.14** (#1c), so R5 stays red. Two pieces still owed when it
  unblocks: the interaction blocks and specialized steps, and the split of
  `RestaurantScreen` into a screen per role (host stand, server terminal,
  kitchen display, storefront, delivery dispatch) — deferred because every
  epic step references its inputs by path, so the split and the epic rewrite
  should land together rather than churn the paths twice.
  **DONE 2026-08-14 except the RestaurantScreen split**, which is still owed:
  R4 and R5 are both green, but RestaurantApp still has one screen carrying
  host, server, kitchen, storefront and delivery controls.
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

## 1d. rc.14's instance-addressing check does not resolve `Id` aliases

**This is why R10 is red, and it is NOT the model's fault. Do not fix it by
editing models.**

rc.14 added a completeness check: a message told to an entity should carry a
field typed `Id(<Entity>)`. It compares the field's *written* type, not its
resolved one, so a field typed by a named alias is not recognised — and the
alias IS the documented idiom (CLAUDE.md § RIDDL Style item 7,
`type OrderId is Id(Order)`), used corpus-wide.

Isolated to a two-command repro, filed as
`../riddl/task/2026-08-14-instance-addressing-check-does-not-resolve-id-aliases.md`:

| command | field type | flagged? |
|---|---|---|
| `DirectCmd` | `thingId: Id(C.Thing)` inline | no |
| `AliasCmd` | `thingId: ThingId`, `type ThingId is Id(C.Thing)` | **yes** |

reactive-bbq went **0 → 111 messages** on the rc.14 upgrade. Of **86 distinct
flagged messages, 72 carry a `*Id`-typed field** and are false positives.

**The other 14 look genuine and are ours to fix once the noise is gone:** the
13 `*Result` types plus `RecordLoyaltyActivity`. The Results wrap a base
record (`result ReservationResult is { reservation: ReservationBase }`)
rather than naming an id, so they may deserve the message — riddl was asked
whether a nested record should satisfy the check.

**It also aborts `sbt checkAll`**, because the same check fires twice in
`patterns/entity/*/example.riddl` and `verifyTemplates` gates before the
suite. Until it is fixed, get the rule state with:

```bash
sbt 'Test/testOnly *ReactiveBbqCompletenessTest'
```

## ~~1b. `constant`~~ and ~~1c. interaction blocks~~ — BOTH CLOSED 2026-08-14

Both were the same defect family: a node written to BAST that could not be
read back. **rc.14 fixed both**, and both are restored and verified in the
full corpus, not just in repros.

- **`constant`** — `PointsPerDollar` is back in the Loyalty context and
  `PointsForSpend` refers to it instead of an inlined 10. riddl's cause:
  `writeConstant` emitted `NODE_FIELD`, stranding the value bytes.
- **Interaction blocks** — `sequence`/`parallel`/`optional` restored in
  `DineInExperience`, **R5 green**. riddl's cause: `InteractionContainer`
  extends `Container` but not `Branch`, so the writer wrote a child count and
  never the children. Their sweep found two more of the same shape
  (`InvariantBlock`, and `relationship` writing no discriminator at all —
  the corpus uses `relationship` zero times, so nothing here was affected).

**The lesson worth keeping: a BAST error names where the reader DERAILED, not
what derailed it.** Bisect file-first, then construct-within-file, and
distrust the construct named. Both defects were found that way, the second in
a single pass because the first had taught the method. A second tell, specific
to this family: **the node count going DOWN when a construct is added** means
children are being lost.


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
