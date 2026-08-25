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

**Phase 3 is DONE** (#1e) — `language-coverage/` is committed and gated.
**Remaining: Phase 5, and R2's orphan briefs.**

**R10's upstream excuse is GONE, and R10 is still red — it is now OURS.**
#1d was fixed on 2026-08-14 and the 49 errors it exposed are cleared, so
reactive-bbq has **zero errors**. R10 demands zero *messages*, and 134
completeness messages remain: the residual bare operands of **#11**, chiefly
the query answers whose `*Result` types wrap a base record with no id field.
**Closing #11 for reactive-bbq is what turns R10 green.**

Measured at **rc.14** on 2026-08-14, every row by running the command:

| item | state |
|---|---|
| reactive-bbq errors / warnings | **0 errors**; 134 completeness messages, now OURS (#11), not upstream |
| degenerate descriptions left | **0** (was 358) |
| `???` bodies | **0** (was 20) |
| BAST round trip | **187/188** at revision 17; the one discrepancy is `shown by` losing its URL through BAST, filed upstream |
| interaction blocks / `constant` | restored and surviving BAST (#1b, #1c closed) |
| terms | **25** (was 2) |
| UI groups / `put` statements | **5** (was 1) / **5** (was 0) |
| rules green | **8 of 10** — R2 and R10 red, both now ours |

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
| R10 | 134 completeness messages, the residual bare operands | **#11** — mostly the wrapped-base-record `*Result` types |

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

---

## 8. Model defects found while triaging riddlg's task — verified, not yet fixed

These came out of `task/2026-08-14-reactive-bbq-names-message-types-where-
values-are-required.md`. **Each was checked against the model here**, so the
next session does not re-derive them. They are independent of that task's
main ask and can be fixed without it.

1. **`SubmittedOrders` is an inlet spelled as an outlet.** riddlg reported it
   as "names no outlet declared in the model", which is a **misdiagnosis** —
   the port exists. `FrontOfHouseContext.riddl:822` declares
   `inlet SubmittedOrders`, and `TableOrder.riddl:790` says
   `send event OrderSubmitted to outlet FrontOfHouse.OrderSplitter.SubmittedOrders`.
   Wrong port *kind*, right port.
   **riddlc validates this cleanly**, which is itself worth reporting upstream:
   a `send … to outlet <an-inlet>` should not pass.

2. **Five entities declare a `morph`/`become` but have exactly one state**, so
   there is no transition to make: `Shift`, `MenuItem`, `MenuRelease`,
   `PurchaseOrder`, `Campaign` — counted with
   `grep -cE '^\s*(initial )?state \w+'` and `grep -cE '^\s*(morph|become) '`,
   which return 1 and 1 for each. **riddlg's task says "4 entities" and then
   lists five**; five is right.
   Either declare the states the entity moves between, or drop the transition.
   Declaring them is probably correct — an entity worth morphing has a
   lifecycle — but that is a modelling decision, not a mechanical fix.

3. **`saga OnlineOrdering.OnlineOrderCheckout` states no timeout**, so a run
   is bounded by riddlg's built-in 60s default rather than by the model.
   Verified: zero `timeout`/`times out` in the saga body. Lower priority.

## 9. Unexplained: a `send` epic step across an existing connector reads as unwitnessed

While writing the Phase 4 epics, this step was rejected:

```riddl
step send command Restaurant.FrontOfHouse.TableOrder.CreateOrder
     from context Restaurant.RestaurantApp to entity Restaurant.FrontOfHouse.TableOrder
```

> no wiring (connector/adaptor/tell) path from 'Restaurant.RestaurantApp'
> reaches 'Restaurant.FrontOfHouse.TableOrder'

**But the connector exists.** `restaurant/domain.riddl:331` declares
`'TableOrderCommand Stream' is from outlet RestaurantApp.AppTableOrderCommands
to inlet FrontOfHouse.TableOrder.TableOrderCommands` — exactly those two
endpoints. The connector carries the `TableOrderCommand` alternation and
`CreateOrder` is a member of it, so **alternation-vs-member matching in the
reachability check is the leading hypothesis**.

**It was dropped, not diagnosed** — the step was removed to get the epic
green. Do not assume the model is at fault. Worth an hour; if it is a riddlc
gap it should be filed, and if it is ours the same shape may be wrong
elsewhere.

Two related rules that ARE correct and were learned at the same time, so they
are not re-litigated: a user may interact only at the application boundary
(`send … from user U to context C` is a hard error), and a `show output X to
user` step must be witnessed by a `put … to X`.

## ~~10. `sbt v` is RED~~ — FIXED 2026-08-14, zero errors corpus-wide

All 49 cleared: 16 wrong-entity aliases retyped, 2 correctly-named aliases
pointed at their entities (which also cleared 38 unrelated "instance is
unspecified" messages), 27 `tell` sites annotated `by <field>`. Detail in
`task/done/2026-08-14-alias-fix-exposes-49-addressing-defects.md`.

Historical detail follows.

## 10-historical. `sbt v` was RED — 16 of 187 models, all from ONE rc.14 check

**Measured 2026-08-14 by running `sbt v`. This is pre-existing and was not
recorded anywhere** — the campaign has been measuring reactive-bbq, which is
unaffected, so nobody had run the corpus-wide CLI gate since the rc.14
upgrade. Nothing in this session caused it; the only local change was an
untracked directory, and the run counts 187 models, not 188.

Every failure is rc.14's instance-addressing check, in its **other** failure
mode from #1d — not "no id found" but *"Event 'X' carries 2 fields typed
'Id(E)' (a, b), so which instance this addresses is ambiguous"*. **Three
classes, and only one of them is ours:**

**Class A — two genuine instances of the same entity (10 sites).** The model
is right and the language cannot say which instance is addressed. Merges,
transfers and renewals inherently name two:

| model | event | fields |
|---|---|---|
| shopping-cart | `CartsMerged` | targetCartId, sourceCartId |
| patient-registration | `PatientsMerged` | survivingPatientId, mergedPatientId |
| digital-wallet | `FundsReceived` | walletId, senderWalletId |
| game-economy | `CurrencyTransferred` | walletId, targetWalletId |
| emergency-dispatch | `IncidentsLinked` | incidentId, linkedIncidentId |
| demand-planning | `ForecastSuperseded` | forecastId, newForecastId |
| policy-administration | `RenewalProcessed` | policyId, newPolicyId |
| treaty-management | `TreatyRenewed` | treatyId, newTreatyId |
| member-enrollment | `EnrollmentTransferred` | enrollmentId, newEnrollmentId |
| audience-management | `LookalikeConfigured` | segmentId, sourceSegmentId |

This is exactly what riddl's `task/done/2026-08-13-tell-to-an-entity-cannot-
name-which-instance.md` is about. **Do not edit these models** — inventing a
single id would destroy the domain meaning of a merge.

**Class B — a CHILD id wrongly typed as the PARENT's Id (13 sites, 8 models).
These are OURS and they are real defects.** riddlc is correct: a task is not a
shift, a report is not an exam, a rider is not a policy.

| model | event | the wrong field |
|---|---|---|
| case-management | `CourtDateCancelled` | `dateId: Id(LegalCase)` |
| case-management | `TeamMemberRemoved` | `memberId: Id(LegalCase)` |
| nursing-workflow | `TaskCreated`, `TaskCompleted` | `taskId: Id(NurseShift)` |
| nursing-workflow | `PatientsAssigned` | `assignmentId: Id(NurseShift)` |
| radiology-workflow | `DraftReportCreated`, `ReportFinalized`, `AddendumAdded` | `reportId: Id(ImagingExam)` |
| policy-lifecycle | `BeneficiaryRemoved` | `beneficiaryId: Id(LifePolicy)` |
| policy-lifecycle | `RiderRemoved` | `riderId: Id(LifePolicy)` |
| member-enrollment | `EnrollmentConfirmed` | `memberId: Id(Enrollment)` |
| supply-chain | `ShipmentReceived` | `receiptId`/`purchaseOrderId` both `Id(SupplyOrder)` |

Fixing means deciding what each child actually is — a distinct entity with its
own `Id`, or a plain identifier — which is a modelling decision per site, not
a mechanical retype. **Not started; needs Reid's call on how far to take it**
(some of these children may deserve promoting to real entities).

**Class C — an actor reference, same entity, not the addressee (3 sites).**
identity-management's `IdentitySuspended`/`IdentityDeactivated`/
`IdentityReactivated` carry `suspendedBy`/`deactivatedBy`/`reactivatedBy`
typed `Id(Identity)`. Those genuinely ARE identities — the admin who acted —
but they are not addressing candidates. Either the check should exclude actor
fields or the model should type them differently. **Worth asking riddl**, since
"who did it" typed as the same entity is a common and correct shape.

**Do not "fix" this by weakening anything.** The check found 13 genuine defects
in one run.

## ~~1e. Phase 3 HELD~~ — LANDED 2026-08-14

**`language-coverage/` is committed and inside every gate.** riddl fixed all six
emitter defects it found (`2ebe24a6c`, `80bb93b40`); each was re-verified here
rather than assumed. One of the six was **refuted and the refutation was right**:
`figma` on a domain or context is a legitimate validation error, and prettify
writing nothing on a validation error is correct — the probe that "found" it had
suppressed stderr.

**It has since found a seventh:** `shown by` loses its URL scheme and host
through BAST (`https://ossum.tech/x` returns as `file:///x`), which is the one
round-trip discrepancy in the corpus. Filed upstream. The model is doing exactly
what it was built for.

Historical detail follows.

**Where it is:** `language-coverage/` in the working tree, **untracked**, with
its `.conf` renamed to `language-coverage.conf.held` so no gate discovers it
(they all enumerate `.conf`). `language-coverage/HELD.md` states this and lists
the four steps to land it. **It is untracked, so `git clean -fdx` would destroy
it** — that is the standing risk of holding it this way.

**Why it is held.** Building it found **six defects in riddlc's source
emitter**, shared by `prettify` and `unbastify`. Filed with repros and code
pointers as `../riddl/task/2026-08-14-prettify-emitter-drops-method-and-shown-
by.md`, with a request to bundle the fixes into the BAST rev 17 change so this
repo regenerates once rather than twice.

| construct | emitter behaviour |
|---|---|
| `method` | **silently omitted** — BAST 11 nodes in, 9 out |
| `shown by` | **silently omitted** — 8 nodes in, 7 out |
| `table of T of [a,b]` | emits `table of T[ a, b ]` — **does not reparse** |
| `attachment N is <mime> …` | emits the mime type **quoted** — does not reparse |
| `figma` on a domain or context | **writes no file**, exits **7**, prints no error |
| `replica of X` | emits `replica ofX` — cosmetic, node count unchanged |

`figma` on a **group** or **type** is fine. The BAST *writer* is correct in
every case; this is an emitter-only class, unlike #1b/#1c which were writer
defects.

**Two lessons worth more than the model:**

1. **`reparses` is NOT `round-trips`.** `method` and `shown by` reparse
   perfectly *because they are gone*. Any check of this kind needs a content
   assertion as well as a parse.
2. **The node-count tell generalises.** Add the construct, bastify, and watch
   the count — it caught all six, exactly as it caught #1b/#1c.

**What the model covers**, once landed: `module`, `version`, `graph of`,
`table of`, all three `replica of` arms, `method`, the three `attachment`
forms, `described at`, `described in file`, `figma`, `shown by`. Grepped
2026-08-14: the corpus uses **none** of them. Two apparent exceptions were
prose, not syntax — `table of` matched *"no table of that size"* and all 11
`attachment` hits were field names.

**`nebula` is deliberately NOT covered.** The grammar marks it DEPRECATED
(`ebnf-grammar.ebnf:68-71`, "Use `module` instead"), and covering it would emit
a deprecation message, contradicting scoping decision 4 and turning R12 red.
`module` is its replacement and is covered instead.

**Also found while probing, and worth keeping:** `described at` **rejects a
trailing slash** — `https://ossum.tech/docs/riddl/` fails, the same URL without
it parses, though the EBNF's `url_path` admits `/`. Reported in the same task.


## ~~11. 495 bare message operands~~ — CLOSED 2026-08-15

All 495 became `prompt(...)` typed holes; the corpus validates with zero errors
under the Error severity. **What survives is the modelling half**: the `*Result`
types wrap a base record and carry no id field, which is why they needed a
prompt rather than a constructor, and which still costs 259 completeness
messages and keeps R10 red. Tracked as #13.

Historical detail follows.

## 11-historical. 495 bare message operands, 269 needing MODEL changes

From `task/2026-08-14-bare-message-operands-now-warn-corpus-wide.md`, which is
**still open** — 15,273 were migrated, these were deliberately not.

- **269 entity query answers.** `reply result R` / `tell result R to entity`
  where R wraps a base record and has no fields to construct from —
  `MarketplaceOrderResult` has exactly one field, `marketplaceOrderData`. riddl
  has ruled a wrapped base record does **not** satisfy the addressing check
  either, so this is the SAME job as the 13 `*Result` types plus
  `RecordLoyaltyActivity` from the alias task. **Do it once, not twice.**
- **162 `on init`/`on other`** — no value in scope. An entity's creation event
  cannot be sourced from the state it is about to populate. May be genuinely
  unsayable; worth asking riddl whether `on init` should be exempt as
  field-less messages already are.
- **~64 handlers emitting an unrelated message** where no field of the handled
  message feeds the target. A domain decision each.

**riddl will not flip the bare form to an Error until this is clean**, so there
is no deadline — but they are waiting on us.

## ~~12. Phase 5 unmeasurable~~ — RESOLVED 2026-08-15

riddl un-blinded the check; it reports **863** corpus-wide, matching the
baseline recorded here before it went blind. Phase 5 is measurable again from
the validator, and the recorded number was independently confirmed correct.

Historical detail follows.

## 12-historical. Phase 5's population was not measurable by the validator

The populates-repository warning **only fires on a `MessageRef` operand**, so
migrating to the `ValueRef` arm blinded it: 863 -> 9 corpus-wide with no model
change. Verified by reverting a single site and watching the warning return.

**The number, taken before the migration, is 854.** Those sites are still
defective. Filed upstream
(`2026-08-14-valueref-migration-blinds-the-populates-repository-check.md`);
until it is fixed, enumerate them from git history at commit `5002d44f~1`, not
from a validator run.


## 13. `*Result` types wrap a base record and carry no id — 259 completeness

The one modelling job left from the message-value migration, and **what keeps
R10 red**.

`result MarketplaceOrderResult is { marketplaceOrderData: MarketplaceOrderData }`
has no id field, so riddlc cannot tell which instance it addresses, and there
was nothing to construct it from — which is why those 269 sites needed a
`prompt(...)` rather than a constructor.

riddl ruled (2026-08-14) that a **nested record does NOT satisfy** the
addressing check: the id must be a field of the record actually named, because
seeing through nesting is an unbounded search. So the fix is to give each
`*Result` a field typed with the relevant id.

This is the SAME job as the 13 `*Result` types plus `RecordLoyaltyActivity`
riddl asked about in the alias task. **Do it once, not twice.**

## ~~14. 90 `MessageFlowPass` warnings~~ — FIXED UPSTREAM in rc.15

Gone. Corpus warnings fell 971 -> 869 and reactive-bbq's 58 -> 1 on the upgrade.

Historical detail follows.

## 14-historical. 90 `MessageFlowPass` warnings

`MessageFlowPass` cannot resolve a `let`-local's message type and reports the
binding name as if it were a type. **0 before the `prompt(...)` migration, 90
after.** Filed as
`../riddl/task/2026-08-15-messageflowpass-cannot-resolve-a-let-local.md`.

45 of reactive-bbq's 58 warnings are these, so R10 cannot go green on our work
alone.

**Four scaffolds failed to reproduce it** — the trigger is not simply "a
`let`-local in a `tell`". The report says so rather than guessing, and points at
`education/corporate-training/training-administration/Training.riddl:784`.


## 15. R10 is 16 items away, and they are all #13 plus one connector

reactive-bbq now validates with **0 errors, 1 warning, 15 completeness** — down
from 111 messages on 2026-08-14. R10 demands zero of everything, so what stands
between the campaign and 9 of 10 is now enumerable:

- **13 `*Result` types + 2 Campaign commands carry no id field** — this is #13,
  unchanged, and it is the whole of the completeness count.
- **1 warning**: the new `ToNotificationService` adaptor's tell target
  `Restaurant.NotificationService` is not reachable via a connector. It replaced
  five identical warnings inside the DeliveryOrder entity, so the count fell
  5 -> 1, but the question it raises — how an external context is reached — is
  unsettled. CLAUDE.md records that `tell ... to adaptor X` was tried and made
  things worse, so this needs thought rather than a reflex connector.

Doing #13 turns R10 into a one-warning problem. R2 (51 orphan briefs) remains
Reid's end-of-plan item.


## 16. reactive-bbq carries 247 `prompt()` typed holes — expected, not debt

Recorded so nobody "fixes" them by inventing values. Every declared field of
every constructed message and morph record in reactive-bbq is supplied
(2026-08-18, `77a4f564`); 247 of those values are `prompt("...")` typed holes.

That is the sanctioned spelling for a value the model genuinely decides at
generation time, and riddl's own constant work describes it that way. The
alternative is not a better model, it is an invented one — the thing riddlg
explicitly asked us not to do.

**The measurement trap, since it cost real time:** a naive
`\(([^)]*)\)` constructor regex cannot see past the nested parens of a
`prompt(...)` argument, so it reports fields as unsupplied when they are not,
and a second edit pass driven by it will CORRUPT lines it already filled. Use a
paren-balanced scanner (`scratchpad/gap2.py` pattern) for any future sweep of
constructor arguments.


## 17. rc.16's Completeness 4b is a REGRESSION — do not model around it

`Handler 'X' in Repository 'Y' handles messages but does not dispatch to any
entity via 'tell'`. Filed by riddl-examples as an rc.16 regression with a root
cause: `ValidationPass.scala:4589-4610`, a check deliberately restricted to
Sinks that now fires on repositories and projectors. We appended corroboration
rather than opening a second ticket.

**It hit us 3 times in 190 entry points, not because our repositories are
better but because most already carry an unrelated `tell` in the same handler**
— they pass incidentally.

Two were worth fixing anyway and are fixed: the `patterns/` examples' results
wrapped a base record with no id, so `CartResult` and `AccountResult` now carry
one. **If 4b is reverted we may return those two repositories to `reply`** —
both spellings are idiomatic here — but the id fields stay, because they are
#13's shape.

**The third is deliberately unfixed.** drug-supply-chain's
`SerializationRepository` answers a projection-backed metrics query; there is no
entity instance to address and no id that would mean anything on the result.
Inventing a target would be worse than the message. It is completeness, not an
error, and blocks nothing.

**Worth remembering:** this reached us as a `sbt v` failure even though the
corpus was clean, because `verify-templates.py` fails the examples on ANY
finding. That is the third time `patterns/` has caught something the 188-model
sweep could not see.


## ~~18. Two riddlc contradictions~~ — FIXED in rc.17, corpus at ZERO

Both were fixed upstream in `c075f1af0`, on the reading Reid gave: the
`persistent` check must fire on **crossing** an external context, not touching
one. With the Error gone the keyword was simply removable, and the adaptor
advisory stopped firing on its own.

**The corpus now validates with zero messages of any kind and `checkAll` is
fully green — all 10 rules.** BACKLOG #1's campaign is complete: R10 and R2 are
both green, and #13's addressing work landed with it.

Historical detail follows.

## 18-historical. Two riddlc contradictions blocked the last 24 messages

The corpus is otherwise at zero. **Neither can be fixed here**; both were
verified to have no legal spelling, and both are filed to `../riddl/task/`.

1. **`persistent` required and not needed** (12 warnings). A connector wholly
   inside an `external context` draws an Error without the keyword and a Warning
   with it. Reid's reading, confirmed by the paths: both ends are `Ext.*`, so the
   Error is the bug — it should require *crossing* a boundary, not *touching* an
   external context. **We keep `persistent`.** A 22-line repro sits beside the
   task file.

2. **"Consider an adaptor" is unsatisfiable** (12 style). The adaptor already
   sits behind the boundary; landing a cross-context connector on it is now an
   Error. This is riddl's own unruled **[1.6]**, and CLAUDE.md has recorded this
   advisory as one not to follow since 2026-08-09.

**R10 is now blocked only by these.** reactive-bbq's 19 remaining messages are
all of these two kinds, so when riddl fixes them R10 goes green without any
corpus change. R2 (51 orphan briefs) remains Reid's end-of-plan item.


## ~~19. `sbt checkAll`'s test half needs riddl libraries published~~ — RESOLVED

rc.19 is published, so the libraries resolve and both halves of `checkAll` run
green. The underlying question stands and is worth deciding before the next
staged-only RC: **`riddlVersion` names both the binary and the libraries, and a
staged RC is a binary only.** While the pin names one, the corpus can be fully
verified with the test suite dark.

Historical detail follows.

## 19-historical. checkAll's test half needed riddl libraries published

The suite links `riddl-language`, `riddl-passes` and `riddl-utils` at
`riddlVersion`. When that pin names a **staged, unpublished** RC — as it does now
at `2.0.0-rc.17-10-59e5d7f5` — the libraries do not resolve and `checkTests`
cannot run at all:

```
not found: .../riddl-utils_3/2.0.0-rc.17-10-59e5d7f5/riddl-utils_3-...pom
```

`sbt publishLocal` from the riddl checkout fixes it. The CLI half
(`riddlcValidate`) is unaffected because `riddlcPath` uses the staged binary
directly, which is why the corpus can be fully verified while the suite is dark.

**Worth deciding:** whether `riddlVersion` should keep serving both roles. A
staged binary and a published library set are now routinely different things, and
the pin cannot name both.


## ~~20. The delivery campaign~~ — DONE 2026-08-24, corpus at ZERO

Closed. The corpus reports **0 findings at every severity across all 188 models**,
`sbt v` passes models and `patterns/`, and `check-repository-ports.py` reports 0
violations. Verified 2026-08-24 against riddlc `2.0.0-rc.24-3-40c0574f`.

Route taken: 3,521 -> 0. The single largest move was 1,744 `on <e>: event E`
clauses, which cleared 3,445 findings at once because both ruled tell-shapes
converge on the entity owning the clause. Repositories now take commands and
queries only, via a projector.

What it taught is in NOTEBOOK; the durable rules are in CLAUDE.md. **Two rulings
came out of it that are accepted and NOT implemented — items 23 and 24 below.**

## 23. Repository command naming — Reid picked option A, NOT STARTED

**Ruling (Reid, 2026-08-24).** `Persist<Event>` is wrong three ways:

1. **past tense dominates** — `PersistTeamCreated` reads as an event, because the
   event name is longer and ends the phrase
2. **`Persist` is a lazy verb** — Reid: *"the equivalent of saying Do to a
   repository, because the only thing it CAN do is persist data. Aren't things
   ever created, deleted, changed, saved?"*
3. **they carry only an id** — `PersistTeamCreated(teamId)`, one field, so the
   command does not say WHAT to write, only WHICH row. Found while sizing the
   rename; not part of Reid's original objection but the same defect.

**Option A, chosen:** verbs by effect, few per repository —
`CreateLoyaltyAccount` / `UpdateLoyaltyAccount` / `DeleteLoyaltyAccount` — with
the projector mapping many events onto them, and **the command carrying the row
data** rather than just an id. Fixes all three.

Scale, measured: **4,030 uses, 1,669 distinct names.** Rejected alternatives were
B (imperative per event, keeps 1:1, but 1,669 noun-phrase renames is judgement
not mechanism, and leaves (3)) and C (mechanical 1:1, leaves (2) and (3)).

Do it with `riddlc find ... -replace`, not regex — see CLAUDE.md.

## 24. Rejections do not go to a database — HALF DONE, and the rest is ORDERED

**Ruling (Reid, 2026-08-24).** *"Nobody ever sends a message to a database
telling it to reject something... Whoever SENT those messages should not be
sending them and should be dealing with the rejection at THEIR level, not punting
to the database."* A genuine business rejection — a declined card — is different:
it is a real event, stored by its own specific command.

**Done:** 268 state-guard sends removed, the refusal preserved as `error`. The
distinction was measured, not assumed: 268 of 269 carried
`rejectionReason = "<X> does not accept <Y> in this state"`. The one that did not
— `"Point balance is less than the points requested for redemption"`, at
`hospitality/food-service/reactive-bbq/restaurant/LoyaltyAccount.riddl:635` — is
the carve-out and was deliberately left alone.

**Left — and the order is not a preference, riddlc enforces it:**

1. remove the split clauses that still `send`/`tell` rejection events
2. **then** trim the rejection members out of the `<X>Event` alternations
3. **then** replace the persistence projectors' `on other` with an explicit
   clause per member that can actually arrive

Attempting (2) first is refused by riddlc's `-replace` write gate, which restores
every file:

```
outlet ReservationEventSplitToReservationBoard is declared as Type
'ReservationEvent', which does not admit Event 'CompleteVisitRejected'
```

That is how the ordering was found — by the gate, not by reasoning. Remaining
population: 52 `<Command>Rejected` declarations, 97 alternation members, 1 send.

For step (3), `scripts/expand-on-other.py` writes 102 clauses: it derives each
processor's policy from that processor's OWN existing clauses and holds back any
whose clauses disagree. **`on other` was the weak answer** and was hiding real
lifecycle events — `VisitCompleted`, `TicketRouted`, `StationAssigned` — not just
rejections.

## 20a. Original rc.21 framing, superseded

Measured 2026-08-22 against `2.0.0-rc.21`, sweeping all 188 entry points:

```
6,107  Event told to a target that declares no clause receiving it
   64  Command, same
  900  inlet admits a type its owner handles nowhere
```

**Zero errors** — nothing fails to validate. But riddlg cannot generate code for
a message sent to something that does not handle it, so Reid ruled these get
fixed by model change, not by softening the check.

### DONE already: the 207 Results (`7073726b`)

All 207 were one shape — inside `on query`, an entity telling the answer to
**itself**. Every one became `reply`, which also required the `replies`
declaration the rc.19-5 rule wants. **None wanted the `on result` clause** the
task warned against.

### RULED — the 900 inlets (Reid, 2026-08-22)

**Implement the `on` clauses. Do not delete inlets.** An inlet's type is often an
**alternation**, so the clause set must cover **every member**. An inlet may be
deleted only on proof that nothing connected to the feeding outlet — *including
through a merge* — ever sends that type, and proving that is harder than writing
the clauses.

### RULED — both tell shapes (Reid, 2026-08-22)

Reid's rationale, and it decides both: **"handling the event is important to be
able to persist it."** An event nothing handles cannot be applied on replay, so
the entity that owns the event is the thing that must carry the clause.

**Shape 1 — an entity's command handler tells ITSELF the event → option A,
convert to `yield`.** This is the correct event-sourced idiom and the largest
change, because it is not a one-line substitution. Each site needs all four of
riddlc's event-sourced rules satisfied at once (CLAUDE.md § Event-Sourced
Entities):

1. the **command's type** declares `yields event E` — `CreateOrder` at
   `commerce/marketplace/order-orchestration/MarketplaceOrder.riddl:47` declares
   none today
2. the entity gains an `on event E` clause to apply on replay
3. the `morph`/`set` **moves out of the `on command` clause into `on event`** —
   at `:652` the `morph` currently sits beside the `tell`, and only `on event`
   may mutate state
4. the `tell … to entity <self>` goes away, replaced by `yield event E(…)`

The 251 entity→itself sites in the sample are this shape. Expect the count to
move — that proportion is from **25 models, not the corpus**.

**Shape 2 — a split forwards an event AND tells the entity back → option B,
add `on event` to the entity** (`OrchestrationContext.riddl:516`). Keep the
tell; give the entity the clause that receives it. Accepted consequence: this
creates **entity → split → entity**, and **riddlc has no cycle detection**, so
nothing will warn if a future edit makes that loop do real work. The clause
should apply the event, not re-emit.

The two rulings converge on the same end state — **every entity carries an
`on event` clause for each of its own events** — which is also what the 900
inlets need. Do the inlets and shape 2 together where they touch the same
handler.

## ~~22. `patterns/` was never migrated~~ — RESOLVED 2026-08-24, `sbt v` GREEN

Reid ruled: **a repository processes commands and queries, never events.** The
effect of a command is a database update; the effect of a query is a result
response. So projectors send commands to repositories — **add the projector.**

Both examples now carry one, and `sbt v` reports **All 188 models passed** with
`patterns/` green.

- `entity/event-sourced`: added `type AccountRepositoryCommand`, retyped the
  repository's inlet from `Account.AccountEvent` to it, added
  `projector AccountProjection as flow` whose four clauses each
  `tell command AccountRepository.Persist<E>(..) to repository`, and rewired
  entity → projector → repository.
- `entity/aggregate-root`: the same, plus the repository was handling the
  aggregate's **domain** commands (`on command Cart.AddLineItem`) — replaced
  with `Persist<E>` commands it declares itself. Its `GetCart` query stays;
  queries are exactly what a repository should answer.

**Reid's framing of the real risk, which is sharper than the one first filed
here:** an entity MAY send a persist command to a repository directly, but with
a projector also in between there are two write paths and the model is
misconstrued. **One or the other.** Both examples now have exactly one: the
entity emits events and never writes the store.

(The concern originally written here — that a projector makes the example teach
two catalogue patterns at once, `entity/event-sourced` and
`projection/read-model` — is real but minor, and is the price of showing a
correct write path. It is not what mattered.)

**`aggregate-root` lost its `CartEventSource`/`CartEventSink` pair.** Cart is an
`aggregate entity`, not event-sourced, so it has no `on event` clauses and the
sink's `tell lineItemAdded to entity Cart` modelled a replay it never performs.
Removing just the tell trips a different check — *"Handler in Sink handles
messages but does not dispatch to any entity via 'tell'"* — so the pair cannot be
made honest here at all, and a source that re-emits an event into a sink that
hands it straight back is the duplicate processing the campaign removed
corpus-wide. `event-sourced` KEEPS its pair: there the entity really is
event-sourced, the tell lands on a genuine `on event` clause, and it demonstrates
replay.

## ~~26. Corpus drifted from prettify canonical form~~ — FIXED and GATED
## 2026-08-25

396 files across 188 of 188 models were not what `riddlc prettify` emits.
`sbt r` fixed them; `prettifyCheck` stops it recurring.

**The change was proved content-neutral before being trusted.** A naive
whitespace-stripped compare flagged 181 files as differing beyond whitespace —
prettify moves `updates repository X` above the projector's outlet, so text
shifts position. Comparing the **token multiset** instead, which is order- and
whitespace-independent, gives **0 of 396 files changed**. Nothing was added or
removed; the diff is spacing and declaration order.

**`verify-bast-roundtrip.sh` now passes 188/188** — the first time this session,
and the point of the exercise. Its byte-for-byte compare is only meaningful
while the source IS canonical.

### The gate

`scripts/check-prettified.py`, wired as `prettifyCheck` (alias `sbt pc`) and
depended on by `riddlcValidate`, so `sbt v` and `sbt checkAll` both enforce it.
Canary-tested: injecting a single one-space drift makes it exit 1 and name the
file, the line and the wanted text. It then caught a real regression
immediately — a `git checkout` of one file during testing silently reverted it
to its pre-prettify state, and the gate found it.

**Reid's rule, 2026-08-25: always commit prettified code.** Run `sbt r` before
committing model edits rather than discovering it at the gate.

`patterns/` is excluded, matching `riddlcConfExclusions` and the round-trip
script. Its examples diverge from canonical DELIBERATELY — see BACKLOG #3, and
do not "fix" them.

### Filed upstream

`riddl/task/2026-08-25-prettify-should-emit-one-space-before-brace.md` — Reid:
*"Byte non-identical, especially with mere white space changes, is a source of
frustration at best and a source of errors at worst."* prettify emits `is  {`
with two spaces on message and query declarations, one everywhere else, and
`term Name is  "text"` with a trailing space. When it lands: re-run `sbt r`,
regenerate `.bast`. Nothing is blocked meanwhile.

---

## ~~25. Self-referential carry-forwards~~ — RESOLVED 2026-08-24, and the
## framing was wrong

**Closed by the commit that added the creation data to creation events.** Kept
here because the original framing was wrong in a way worth not repeating.

**What this item claimed:** 217 self-referential args across 37 of 57 morph
constructors, "not uniformly wrong", needing per-site judgement.

**What was actually true, measured with `dump --json` across ALL statement
kinds rather than morphs alone:**

```
277 args across 77 statements read a *StateData record
     19 across 16  are in a CREATION clause  <- the defect
    258 across 61  are state-to-state        <- correct, untouched
```

Two corrections to the old entry. The population was **277, not 217** — the
earlier count looked only at `morph-statement` nodes and missed the identical
defect in `yield`, `send` and `set` statements. And the defect subset is **19
args, not 217**: on a state-to-state transition, reading the current record
forward is exactly what the model means, and 258 of these are that.

**The 19 needed no judgement at all, contrary to what this item said.** Two
shapes, both mechanical once the evidence was in hand:

1. **10 `*CreatedAt` args** read a creation timestamp off the record being
   created. A creation event's timestamp is *now*; it became
   `prompt("current timestamp")`.
2. **6 args in 4 corporate entities** — and this is the finding.
   **The creating COMMAND already carried every one of them and the EVENT
   dropped them:**

   | command carries | event dropped |
   |---|---|
   | `CreateMenuItem(menuItemDescription, recipe, pricing)` | all three |
   | `CreateCampaign(campaignDescription, campaignPromotion)` | both |
   | `CreateMenuRelease(releaseDescription)` | one |
   | `CreateBulkOrder(requestedDeliveryDate)` | one |

   So replay genuinely could not recover them and the `on event` clause reached
   for the only thing in scope — a record that did not exist yet. The fix is the
   event-sourcing rule already in CLAUDE.md: the event carries what replay needs.
   The fields were added to the four events, passed through from the command at
   the `yield`/`send`, and read from the event binding in the `morph`.

**The lesson, which is the reusable part:** the "per-site domain judgement"
this item predicted dissolved once the commands were read. A field that looks
like it needs a human decision may just be information the model already has
one hop away. **Check what the neighbouring definition carries before
concluding a value must be invented.**

Verified: 0 creation-context self-references remain; the 258 legitimate ones
are byte-for-byte untouched; corpus at 0 findings across 188/188; `checkAll`
green.

---

## 21. Only `none`/`empty` is a real gap — arithmetic is by design, enumerator is FIXED

Found 2026-08-22 finishing the `set`-value work (#16 in `task/done`).
**Re-measured against `2.0.0-rc.22` on 2026-08-23, and two of the three original
claims did not survive.** The first version of this item asserted all three were
gaps and was quoted back as current fact; check before repeating it.

- **enumerator — FIXED, not a gap.** `set field ShiftData.shiftStatus to Open`
  and the qualified `... to ShiftStatus.Open` both validate at **0 errors** on
  rc.22. The original claim that neither resolves is stale; it was true at the
  rc.19/rc.20 era and was never re-checked.
- **arithmetic — WILL NEVER EXIST.** Reid ruled 2026-08-23: RIDDL does not do
  arithmetic, and `pointBalance + accrualPoints` is what the AI prompt is for.
  A `prompt(...)` hole is the intended form, not a defect. **Do not file this
  upstream again.**
- ~~**absent — a genuine gap, filed.**~~ **FIXED in rc.23.** `empty_value =
  ( "empty" | "none" ) [ !statement_start type_expression ]` — both spellings
  parse to the identical AST and prettify converges them to `empty`.
  **But the cardinality precondition is NOT enforced**: `empty` is accepted on a
  required `TimeStamp` and on a `OrderLine+` just as readily as on a `?` field,
  with no diagnostic at any severity. Filed as
  `../riddl/task/2026-08-24-empty-is-not-checked-against-cardinality.md`.
  Use it only where the field is genuinely optional — riddlc will not stop you.

### What that leaves — 15 prose strings, was 22. CLOSED 2026-08-23

The 7 actionable ones are done and the task is in `task/done`. The 15 that
remain are each remaining for a stated reason, so this item needs no further
work unless the upstream gap closes.

- **10** display-status sites (`reservationDisplayStatus`, `ticketDisplayStatus`)
  are `String(1,30)`, so a string literal genuinely IS the value — not defects.
  The enumerator fix does not apply unless those fields should have been enums.
- ~~**6** `cancellationReason` sites~~ — **DELETED 2026-08-23.**
  **The justification given here was WRONG and was quoted forward, so read this
  correction:** it claimed each was "immediately followed by a `set state ... to
  record OnlineOrderData(...)`". That is true of exactly **one** of the six.
  The other five are followed by `}` or a `when`. The redundancy is with the
  **`morph` on the line ABOVE**, which already carries
  `cancellationReason = onlineOrderCancelled.cancellationReason`. Deleting was
  still correct; the reason was not. reactive-bbq held at 63 completeness /
  0 errors across the deletion.
- ~~**5** `set state TableOrder.*` sites~~ — **DONE 2026-08-24, rc.23 shipped
  `empty`.** Each prose string was a STATE INVARIANT ("in this state
  presentedBillTotal is none") sitting under a `morph` that carried every field
  forward. The invariant is now folded INTO the morph as `presentedBillTotal =
  empty` etc., and the prose deleted — one assignment, not an assignment plus a
  contradicting comment. 10 `empty` uses, all on `?` fields. reactive-bbq held
  at 63 completeness / 0 errors.
  **`orderItems` was NOT emptied**: it is `OrderLine+`, minimum cardinality 1.
  None of the 5 sites actually asked for that — the `orderItems = empty` in the
  original task text came from the *Draft* site, which had already been
  converted to a record constructor.
- ~~**1** `Reservation.Requested.base` record-update site~~ — **FIXED
  2026-08-23**, `restaurant/Reservation.riddl:850`. The prose string, the
  `let ... = prompt(...)` above it and the contentless `morph ... with
  requestedData` all collapsed into one morph constructing the record outright.

**Two constructs proved to work that had NO precedent anywhere in the corpus**
(grep before writing returned zero of each) — worth knowing before anyone
assumes they are unsupported:

- **nested record construction** in an argument list:
  `base = record ReservationBase(...)`
- **depth-3 field paths** through a non-optional field:
  `ConfirmedData.base.reservationId`

Both validate at rc.22, and a **negative control confirmed it is real checking**
— substituting `ConfirmedData.base.bogusField` produced a precise unresolved-value
error at exactly that span. Do not take the green run alone as evidence; that is
what the control was for.
