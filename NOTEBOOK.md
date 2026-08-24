# NOTEBOOK.md - riddl-models

Development journal for active work on the riddl-models repository.

## HANDOFF

**Branch** `release/2`. `main` stays 1.x until riddl 2.0 ships (BACKLOG #4).

**Build state, verified this session:** `riddlVersion = "2.0.0-rc.23"`,
**published**, `riddlcPath := None`.

**There is NO staged/published binary drift, and there never was.** The staged
`../bin/riddlc` and the artifact the plugin downloads are the SAME build,
commit `10788a0a`. Previous handoffs claimed rc.22 and rc.21 drifted from their
tags; that was an artifact of reading `.object.sha` on an **annotated tag**,
which returns the TAG OBJECT, not the commit. Dereference it:

```bash
o=$(gh api repos/ossuminc/riddl/git/ref/tags/2.0.0-rc.23 --jq '.object.sha')
gh api repos/ossuminc/riddl/git/tags/$o --jq '.object.sha'   # -> the commit
```

Checked for rc.22 as well: `3fb1cf37` -> `c9e58031`, exactly what that binary
reported. **Do not re-file this as drift.**

### `sbt v` is GREEN. `checkAll` is RED, and that is the remaining campaign.

```
sbt v        All 188 models passed  +  patterns/ green
collect-warnings.py   3,521 findings   0 errors   17 of 188 models at zero
checkAll     RED - its test half asserts R10: zero errors AND zero warnings
```

The two gates use **different thresholds**, which is not a disagreement:
`riddlcValidate` fails only on errors; the test suite asserts zero findings of
any kind. So `checkAll` is red on the 3,503 completeness findings — the
campaign's ruled main body, "an entity is told an event and declares no clause
receiving it". Unfinished, not regressed.

### Landed this session

- **rc.23 upgrade.** Identical results to rc.22 (3,521 / 0), no regression.
- **`empty` shipped in rc.23** and closed the last blocked item of BACKLOG #21.
  Grammar: `empty_value = ( "empty" | "none" ) [ type_expression ]`; both
  spellings give the same AST and prettify converges them to `empty`.
- **BACKLOG #22 resolved** on Reid's ruling — repositories process commands and
  queries, never events; projectors send the commands. Both pattern examples now
  carry a projector. `sbt v` went green as a result.

### Traps banked — all cost real time

- **`empty` is NOT checked against cardinality.** It is accepted on a required
  `TimeStamp` and on `OrderLine+` with no diagnostic at any severity. Filed as
  `../riddl/task/2026-08-24-empty-is-not-checked-against-cardinality.md`. Use it
  only where the field is genuinely `?`.
- **A `str.replace` whose anchor does not match silently changes nothing**, and
  the validation that follows is of an UNMODIFIED file. This produced a false
  "rc.23 accepts empty on a required field" reading before it was caught. Always
  `grep -c` the substituted text before trusting the run that follows.
- **Multi-line quoted strings need a RUNNING quote total**, not a per-line
  parity test — the first attempt dropped 2 lines of each 5-line prose string
  and orphaned the rest.
- **Verify the riddlc PATH.** `../../../bin/riddlc` from a 3-deep model dir
  resolves inside the repo where nothing exists; the command fails and a
  counting pipeline prints `0`. Hit again this session.
- **A parse error ABORTS the file**, so the rest of that model is unmeasured.
- **`reascribe.py` runs LAST**, after wiring.
- **Zero means zero of EVERY severity** — that is what `checkAll` asserts.

### Certainty

**Verified by command:** pin, staged binary and downloaded artifact all rc.23 at
`10788a0a`; tag-object dereference for rc.23 and rc.22; `sbt v` green over 188
models plus patterns; 3,521/0; both pattern examples clean; reactive-bbq at 63
completeness / 0 errors before and after the `empty` conversion.

**Assumed, not verified:** that the 3,503 completeness findings are only the two
ruled tell-shapes — top of a frequency count, not an exhaustive audit.

### `task/` — two files

- `2026-08-22-handle-the-messages-you-are-told.md` — **in progress**, the above
- `2026-08-20-regenerate-checked-in-bast-after-2.0.0.md` — **blocked**; 2.0.0 has
  not shipped (newest is rc.23, a prerelease). All 190 tracked `.bast` are
  revision 19 and the reader wants 20

**Run `/ossuminc-skills:check-tasks` in the new session.**

---

## Incoming Tasks

**At session start**, check the `task/` directory for pending
work requests from other projects. Each `.md` file describes a
task (e.g., dependency upgrade). Treat unresolved tasks as to-do
items unless already completed (verifiable from this notebook,
CLAUDE.md, or git log). After completing a task, append results
to the task file and note completion in this notebook.

---

## Current Status

**Date**: 2026-05-18
**Phase**: riddlc 1.23.0 — Handlers Completed, BAST Tracked

- **187 models** validated with riddlc 1.23.0 — zero errors
- Handler placeholders (`prompt "..."`) replaced with concrete
  `tell command/event X to entity Y` messaging across all models
- Missing commands/queries/results added to entities for a
  complete operational surface
- Canonical RIDDL prettify form unchanged from 1.16.5/1.17.1 to
  1.23.0 (verified on shopping-cart: byte-identical output)
- Build uses **sbt-riddl plugin** at 1.23.0
- `.bast` files **are tracked** and regenerated via `sbt b`
- `validateOnCompile = false` in build.sbt — validation must be
  invoked explicitly via `sbt v` / `sbt riddlcValidate`
- All model READMEs have NAICS codes

### In Progress: `release/2` — A6 tell-reachability

Branch `release/2` migrates the corpus to RIDDL 2.0 streaming
syntax and wires every `tell` target so it is reachable via a
connector (A6). Validate with `../bin/riddlc-13cc4baa` — it
misreports its own git hash but is the latest `riddl` build.

Gate over all 187 `.conf` entry points as of 2026-07-26:

| metric | at `cc6902c` | now |
|---------------|-------------:|----:|
| errors | 0 | 0 |
| deprecations | 0 | 0 |
| completeness | 0 | 0 |
| unreachable | 98 | **0** |

**A6 is complete.** The 14 warnings that remain are the same 14
that predate this work (verified by diffing normalized message
text against the baseline): 10 "cross-context references violate
the 'bounded' aspect" path warnings and 4 port-overload warnings.

Class B (30 warnings, second-and-subsequent repositories) is
**done**. The defect was misrouting, not omission: the generator
in `task/wire-a6-reachability.py` wires only `repos[0]`, so events
belonging to a sibling repository were connected to the wrong one.
Fixed by re-pointing existing connectors, using two affinity
signals — a projector's own `updates repository X` clause (exact),
and the repository handler's `on command Entity.*` set. `Reporting`
was never wired at all: the generator requires a context to have
entities, and that context has three repositories, three
projectors, and zero entities.

Newly wired repositories get **inlets only, no `Responses`
outlet** — reachability needs only an inbound connector, and
adding app-side response ports is what caused the port-name
collisions in an earlier, reverted attempt.

Class A (68 warnings, whole contexts as `tell` targets) is
**done**, but only 10 of them were what the plan assumed. 58 were
a context or entity telling **itself**, where a connector would be
a self-loop modelling something untrue. Two idioms, and they are
not interchangeable:

- **entity tells its own context** (8) → `send event X to outlet
  <entity's event outlet>`. `yield` does *not* work here: it
  clears the unreachable warning but raises `[completeness]`
  "Command processing in Entity E should result in sending an
  event". Entities must emit through a port.
- **external context tells itself** (50) → `yield event X`.
  Contexts are not bound by that entity rule, so this is clean.

The 10 genuine cross-context tells got an inlet on the target, an
outlet on the source, and a domain-scoped connector carrying
`option is persistent` (spec §7.3). Where the source was already
an `adaptor` (ticket-sales `MarketingAdapter`), the adaptor itself
carries the outlet.

Two things worth knowing next time:

1. **Compiler bug (riddl).** `ValidationPass.scala:441` checks
   only `SendStatement`/`TellStatement` for the command→event
   completeness rule, while the `QueryCase` arm immediately below
   it also checks `YieldStatement`. `yield` was wired into the
   query branch when A22 landed and the command branch was
   missed. Filed as `../riddl/task/`. Once fixed, `yield` becomes
   legal for entity command handlers too — though `send ... to
   outlet` stays the better model, since that is what puts the
   event on the wire to repositories and projectors.
2. **Latent gap.** `OrderFulfillmentSaga` tells four external
   contexts cross-context, yet the compiler emits *no*
   unreachable warning for tells inside a `saga`. Reachability
   appears not to traverse saga steps. Those 8 sites are
   unwired and invisible to the gate.

Note: `riddlc-13cc4baa` reports 2 pre-existing `[missing]`
warnings in `healthcare/clinical/appointment-scheduling` (schema
`AppointmentData` lacks metadata and a description) that older
binaries did not flag. Unrelated to A6.

### 2026-08-01: riddlc 2.0.0-rc.8 — error-sink inlets

rc.8 requires every domain to name a destination for hard errors:
an inlet accepting `Riddl.GeneratorError` and carrying `option
error-sink()`. Without one the domain draws a `[missing]`
warning — 190 of them, one per domain, across the whole corpus.

Three constraints shaped the fix, each found by testing rather
than assumption:

1. **A domain body does not admit an inlet.** Only `connector`,
   `context`, `application`, `epic`, `author`, types and includes.
   So the inlet lives in the domain's application context and the
   connector, which a domain body *does* admit, sits beside it.
2. **The inlet must be connected**, or it draws `Inlet 'ErrorSink'
   is not connected`. Upstream is `Riddl.ForeverEmpty.void`, the
   predefined source that never emits — the honest statement that
   no modelled component produces a `GeneratorError`; generators
   do, at run time. That is what the predefined pair is for:
   `ForeverEmpty` as placeholder producer, `BottomlessPit` as
   placeholder consumer.
3. **An arity-ascribed context cannot host one.**
   `api-management`'s `application context APIManagementApp as
   flow` is fixed at 1 inlet / 1 outlet; adding the sink made it
   `merge` and errored. Its sink moved to the plain sibling
   context `APIContext`.

`reactive-bbq` is left with 3 `[missing]` warnings that **no model
edit can clear** — the two error-sink checks contradict each other
for nested domains. The missing check is per-domain and names
`Restaurant`, `BackOffice` and `Corporate` individually; the
uniqueness check is scoped to the *root* domain, so giving each
subdomain a sink yields "second 'error-sink' in Domain
'ReactiveBBQ'". One sink → 3 warnings; four sinks → 3 errors.
Warnings being preferable, the root keeps the single sink, hosted
in a new `ChainOperations` context since the umbrella domain owns
no application of its own. Filed upstream as
`../riddl/task/error-sink-checks-contradict-for-nested-domains.md`.

Gate at rc.8, all 187 models: **0 errors, 0 deprecations, 0
completeness, 0 usage, 0 warnings**, 3 `[missing]` (the
unsatisfiable ones above), 0 nonzero exits. Round trip 187/187
with zero discrepancies.

Two canonical-form details worth remembering, both caught by the
round trip rather than by validation:

- `option error-sink` parses but canonicalizes to
  `option error-sink()`
- a connector's canonical form is the single-line
  `connector X is from outlet A to inlet B with { ... }`, not a
  braced body

### 2026-08-02: event sourcing — reactive-bbq converted in part

The staged binary promotes entity semantics from options to keywords
(`event-sourced entity Order is {`) and enforces four preconditions of
event sourcing as errors, gated on that intention:

- **R1** every handled command's TYPE declares `yields`
- **R2** every event so named has an `on event` clause to apply on replay
- **R3** `set`/`morph`/`become` only in `on event` — `on init` included
- **R4** a foreign event may not touch state; it yields one of ours first

**The recipe**, validated on `InventoryItem` and then applied:

1. `entity X` → `event-sourced entity X`
2. add `yields event E` to each handled command's declaration
3. the existing self-`tell event E to entity <self>` becomes `yield event E`
   — that statement always *was* "apply this event", `yield` is its name
4. `morph`/`set` move out of the command clause into `on event E`
5. `on init { set state S ... }` → `on init { yield event <Creation> }`,
   with the `set` moving to `on event <Creation>`

Two things that constrain the shape, both established by testing:

- **`on init` cannot be dropped.** R3 forbids `set` there, but a state with
  an empty body is a parse error, so the init handler must stay. `yield` is
  legal in it, which is what makes step 5 work.
- **A repository must not handle a domain command.** `yields` is optional,
  and it belongs to a *domain* command: it says what handling that command
  records. A repository stores the consequence; it does not decide it. The
  corpus had repositories handling the entity's own commands, which only
  showed up as a conflict once R1 put a `yields` on them. Each such
  repository now has its own `Persist<Event>` commands, declaring no
  `yields` — the idiom `ReportingContext` already used with its `Record*`
  and `Log*` commands. A persistence clause writes the stored row
  (`set field Stored<X>.<field>`), which is also what makes it executable
  rather than prompt-only.

**All 13 entities converted.** Model validates clean; round trip 48/48.
83 `yields` declarations, 147 `yield` statements, 268 refusals made
explicit, 30+52 repository persistence commands.

Two more corrections the multi-state entities forced, both the same
category error — a processor that *handles* a command without *producing*
its event:

- **A "to" adaptor translates a source event into the target's command.**
  Saying it handles the target's command made it a false handler, and once
  that command declared `yields` the adaptor was asked to record an event
  it does not produce. Six adaptor clauses now read `on event <Source>`,
  each source picked from the fields the clause's own prose already reads.
  This contradicts CLAUDE.md's older "to adaptors must reference the target
  context's command types" rule, which came from an earlier riddlc.
- **A refusing clause says `error` first.** riddl 0054a8433 exempts a
  clause that refuses, but reads refusal from `error`/`require` — and the
  A23 work had *removed* those errors, leaving refusal implied only by
  sending a `*Rejected` event. The error now precedes the effect, which is
  what A23 asked for in the first place.

The multi-state entities were already most of the way there: the streaming
work had given each state handler `on event E { morph ... }` clauses, so
R2 and R3's morph half were satisfied before this started.

Corpus state under this binary: **clean**. All 187 models validate with
zero findings of every category, 0 nonzero exits; round trip 187/187 with
zero discrepancies; every `.bast` regenerated (FORMAT_REVISION 2 → 3).

**The corpus-wide sweep**, from 194 errors + 27 deprecations to zero:

- 27 entity options became intention keywords (`aggregate event-sourced
  entity Claim is {`). The parser stores them canonically sorted and
  prettify emits that order, so they are written sorted or the round trip
  rewrites every one.
- The 10 models that already declared `event-sourced` had the uniform
  shape `on command C { morph to state S; tell event E to self }` with a
  per-state `on init { set state S }`. R2 and R3 are the same move: the
  state change belongs where the event is applied, so each event got an
  `on event` clause holding the morph and the set, and each `on init`
  yields the event that enters its state.
- 45 events enter no state at all — they record something without moving
  the machine — so their `on event` clause applies them to the current
  state rather than naming one.
- Several states have **no modelled transition into them** (a gap that
  predates this work). Their `on init` yields the creation event, which
  for an event-sourced entity is what initialisation means: replay from
  creation.

The same "handles a command it does not fulfil" error recurred in three
more processor kinds, and each was a modelling defect rather than a
compiler one:

- 27 repository clauses across 4 models → their own `Persist<Event>`
  commands. Where two repositories persist the same event, the clause is
  qualified by repository, or the bare name is ambiguous.
- 6 "to" adaptor clauses → `on event <Source>`.
- 1 source and 1 sink relay in `campaign-management`. A `source` has no
  inlets, so an `on command` clause in one can never fire — dead. The
  sink's inlet is typed `CreateCampaign`, so `on other` routes exactly
  what arrives without claiming to fulfil it.

**A trap worth remembering:** the persistence sweep first used a corpus-wide
set of command names, and converted repositories in 47 unrelated models
because `AddItem` is a domain command in reactive-bbq and an ordinary one
in shopping-cart. Name sets must be scoped per model.

### 2026-08-04: task triage — six closed

- **`.synapify/` gitignored.** It had been untracked since 2026-08-01, and
  every commit since was made by excluding it by hand. Real papercut,
  one line.
- **error-sink** — done, but *not* in the shape the task asked for. It
  prescribed a `context Operations`; riddl later withdrew that
  (`cca938268`), and canonical is `option error-sink()` **with parens** —
  the bare form parses but canonicalizes, so it fails the round trip. The
  file is corrected rather than filed as-written.
- **release/2 syntax migration** — acceptance met (0 errors, 0
  deprecations). Its `FORMAT_REVISION 13` references are stale: that was
  BAST version 1, and revision restarted at 1 for version 2. We are on 4.
- **A9 requires/returns**, **connector scope** — both verified done.
- **`main` still 1.x** — closed as *superseded*, not fixed. Synapify now
  reads `release/2` and has a settings panel for it. `main` stays on 1.x
  until riddl 2.0 ships, because `release/2` pins a staged, unpublished
  RC that nobody could resolve from a default branch.

**Open:** `2026-08-04-connector-naming-convention.md` arrived mid-session.
Its claim verified exactly: **1287 of 1705** connectors are named
`Link<Source>To<Target>`, 76 of them in reactive-bbq.

### 2026-08-04: `sbt test` works — a second, independent gate

The Scala suite had never compiled since the first commit. Now wired up
and green: **189 test cases, 187 models plus the 2 pattern examples.**

Three things had to be true, and each was a small discovery:

1. **Dependencies.** `riddl-language`, `riddl-passes` and `riddl-utils`
   at `riddlVersion`, resolved from the local ivy that riddl's
   `publishLocal` fills. One `riddlVersion` val now pins both the binary
   and the libraries, since they come from the same build.
2. **Scala version.** This project was on 3.8.4 and riddl publishes with
   **3.9.0-RC4** — newer TASTy is not readable by an older compiler, so
   `Test/compile` failed with "TASTy file ... could not be read". Note
   riddl's own `build.sbt` comment claims 3.8.4; `V.scala` is the truth.
3. **The suite validated the wrong unit.** It walked every `.riddl` file,
   which would fail on ~800 `include` fragments that begin at `context`
   or `entity` and cannot parse alone. It now iterates the file each
   `.conf` names in `input-file` — a model, not a file. That also picks
   up the two pattern examples for free.

It is not a duplicate of `sbt v`: this links the library and calls
`Riddl.parseAndValidate` in process, where riddlcValidate shells out to
the binary. A disagreement between them would itself be the finding.

**`sbt test` is a weak gate for model edits.** sbt 2 routes `test` to
`testQuick`, which skips tests it believes unchanged, and this suite
reads `.riddl` files at run time so sbt never sees a model change as an
input. Hence `sbt checkAll` (`riddlcValidate` then `Test/executeTests`),
which forces all 189. The `verifyTemplates` hook had to move from
`Test / executeTests` to `Test / test` for the same reason — `sbt test`
never routed through executeTests at all.

Also fixed: the suite used the deprecated `RiddlParserInput.fromPath`,
which throws; `fromPathSafe` returns the failure so an unreadable file
fails the test with its reason.

### 2026-08-04: riddlc 2.0.0-rc.9-48-fdc5c171 — BAST revision 4

`sbt v` green on the first run again: 2 pattern examples, 7 templates,
187 models, 0 findings. No source change was needed — moving
`requires`/`returns` from `Function`/`Saga` fields into contents
(`3e4af6801`) is an AST change that leaves the surface syntax alone, and
the saga template that uses both still parses untouched.

What it did move is the wire format: `FORMAT_REVISION` 3 → 4, so **all
189 `.bast` regenerated** — the 187 models plus both pattern examples.
Round trip 187/187 with zero discrepancies, and both pattern examples
unbastify to valid source.

Note the revision numbering restarted at 1 for BAST version 2, which is
safe only because the version moved with it: `Header.isValid` checks
version first, and no file carries version 2 from before. It must not be
renumbered again within version 2.

### 2026-08-03: riddlc 2.0.0-rc.9-42-37b0db94 — nothing broke

First upgrade where the build automation carried the check. `sbt v`
covers the whole repository now, and it was green on the first run: **2
pattern examples, 7 templates, 187 models, 0 findings**; round trip
187/187.

The syntax change in this build **relaxed** a rule rather than tightening
one. `867ab0333` lets a saga body hold comments and types, like every
sibling container — the restriction we hit writing the saga template was
"a rule disagreeing with its own AST", since `OccursInSaga` always
admitted `Comment`. `sagaDefinitions` was the one container in its family
that did not lead with `vitalDefinitionContents`.

So the note in the saga template saying comments do not parse there is
gone, and the explanation of compensation ordering moved back to where it
belongs: directly above the steps it explains. That is the placement the
riddl commit argues for, and it was only ever outside the saga because
the parser forced it there.

181 `.bast` regenerated — the parser-input hash memoisation
(`496e77c39`) changed their content, though the round trip is unaffected.

### 2026-08-03: the patterns check is wired into the build

`sbt verifyTemplates` runs `scripts/verify-templates.py`, and
`riddlcValidate` depends on it — so `sbt v` now means the whole
repository. Verified end to end: exit 1 with a broken template, exit 0
when fixed, and it re-runs rather than caching.

The script also grew to validate the two pattern **examples**, since
`riddlcConfExclusions := Seq("patterns")` hides those from
`riddlcValidate` for the same reason it hid the templates.

Three things this turned up:

1. **`riddlcVersion` pointed at a version that cannot be downloaded.**
   The staged `2.0.0-rc.9-34-5488fd9d` is not published, so `riddlcBinary`
   failed with a bare `Nonzero exit value: 56` — meaning `sbt v` had been
   broken for anyone since the pin, while the corpus was being validated
   with `../bin/riddlc` directly. `riddlcPath` now prefers a staged binary
   when present and falls back to the download.
2. **Two `Def.uncached` needs.** A `Unit` task with no hashable inputs
   runs once and is then cached forever, and `Tests.Output` has no
   `JsonFormat` at all — the same sbt 2 caching trap filed against the
   plugin in July.
3. **The Scala test suite has never compiled.** It imports
   `com.ossuminc.riddl.language/passes/utils`, and `build.sbt` declares no
   `libraryDependencies` at all. It dates from the first commit. Left
   alone; the `Test / executeTests` hook is in place for when it is fixed.

There is no CI in this repo — `.github/` holds only `FUNDING.yml` — so
this task is the automation. riddl's own CI validates the corpus
externally via `validate_external_riddl.py`.

### 2026-08-03: a substitution harness for the pattern templates

`scripts/verify-templates.py` makes the seven `template.riddl` files
checkable for the first time. They were unreadable by riddlc for two
reasons at once — they carry `{Placeholder}` names, and they are
*fragments* that begin at `entity`/`saga`/`projector`, not at `domain` —
so nothing had ever checked them, and they had drifted to pre-2.0 syntax
while the 187 models were kept green.

The harness substitutes ordinary values (Order, Cart, Item), wraps each
fragment in the smallest scaffold that makes it a whole model, and runs
riddlc. **All seven now parse; they did not before — 0/7 at baseline.**

Two tiers, deliberately:

- **parse is the gate.** It is what these files actually failed, and it
  catches exactly the rot that happened.
- `--validate` is a source of suggestions. Making a bare fragment
  validate as a whole model needs a scaffold so large — sink, repository,
  source, connectors — that it starts testing the scaffold. So findings
  naming a scaffold definition are classified and ignored, and what
  remains is about the template. Some of that is inherent to being a
  fragment: an entity template cannot declare its Id type "in the
  containing context" when it has no context, nor connect its own outlet.
  2 of 7 validate cleanly today.

An unknown `{Placeholder}` fails the run rather than silently
substituting nothing — that is the maintenance guard, and it is tested.

What the rewrite had to fix, all of it invisible until now: `option
event-sourced` as an option, `briefly` outside a `with` block, `state X
is { fields }` instead of `of record`, comma-separated aggregate fields,
`{Child}*` for `many`, and `@Cmd.field` references. Two parser facts
worth keeping: a saga's `requires`/`returns` belong to the **saga**, not
to a step — a step's body is statements, its compensation is spelled
`reverted by` — and a **comment between `returns` and the first `step`
does not parse**. Also `???` is for a wholly empty body; it cannot follow
another statement.

### 2026-08-03: riddlc 2.0.0-rc.9-34-5488fd9d — patterns/ caught up

Gate and round trip both clean on the upgrade with no model changes:
187 gated models, 0 findings, round trip 187/187.

The work was in **`patterns/`**, which `build.sbt` excludes from
`riddlcValidate` (`riddlcConfExclusions := Seq("patterns")`) and which the
round-trip harness skips too. The two pattern *examples* have `.conf`
files and had therefore gone unchecked through every upgrade in this
migration. Validating them explicitly found:

- both carried a deprecated `option aggregate()` and no error-sink inlet
- **the event-sourced pattern did not declare `event-sourced`.** The file
  that exists to demonstrate the idiom — whose own prose says "every
  balance change is recorded as an event" — was a plain aggregate. Now
  `aggregate event-sourced entity Account`, satisfying all four rules,
  with its repository moved to `Persist<Event>` commands.

Full gate including patterns: **189 models, 0 findings.**

Two things deliberately left alone:

- The seven `template.riddl` files are parameterised with
  `{Placeholder}` names and do not parse by design. No `.conf`, so
  nothing gates them.
- The pattern examples are hand-formatted for readability (wrapped
  alternations, `Decimal(12, 2)`), which differs from canonical form in
  151 lines. Canonicalising would emit 341-character alternations and two
  ports per line — the prettify quirks already noted — and these files are
  documentation. Their `.bast` is regenerated; their formatting is not.

**Lesson:** an exclusion in `build.sbt` is invisible to the gate that
reads it. Anything excluded needs its own check, or it silently rots
through every upgrade.

### 2026-08-03: riddlc 2.0.0-rc.9-29-989b7f46 — both sink gaps closed

**187 models, 0 findings of any category, 0 nonzero exits, round trip
187/187.**

The four split/merge/flow tell-dispatch warnings are gone — `30979985d`
restricts that check to a Sink, which was the answer to our task. The Sink
check itself was answered "right as written" (`9c6546945`): connecting an
app straight to an entity's inlet **is** an inbound stream that has not
been modelled, and it hides the context boundary inside whichever entity
happens to be the first target. Both outliers were real gaps.

**Delivery.** The `ToDelivery` adaptor reached across the boundary into
`Delivery.DeliveryOrder`. Now `OnlineOrderPipeline` gains a
`DeliveryFulfillments` outlet, a domain-scoped `persistent` connector
carries it to a new `DeliveryIntake` sink, and that sink does the
translation the adaptor used to do. The adaptor is gone; its
`DeliveryRouted` notification moved to the pipeline. The pipeline became
`as split` — two outlets is a split's arity, not a flow's.

**Inventory.** Three approaches failed before the right one:

1. A cross-domain connector from Corporate's supply chain is **not
   allowed** — "a connector that crosses a domain boundary indicates a
   failure of domain analysis". Cross-domain integration in this model is
   done with adaptors and `tell`, never connectors.
2. Routing the app's connector through a sink and dropping the entity's
   inlet broke A6: a sink has **no outlets**, so it cannot connect onward,
   and the entity became unreachable.
3. What worked follows the domain's own existing pattern. `HRSystem` and
   `AccountingSystem` are already modelled as external contexts with event
   sources feeding sinks. What actually replenishes inventory is a
   supplier delivering stock, so `SupplierSystem` joins them, and its
   `StockDeliveries` outlet feeds a new `StockReceiptSink` that turns a
   delivery into `ReceiveStock`.

The upstream-path check walks `Streamlet` adjacency only, so an **adaptor
breaks the chain** — a sink fed via an adaptor still reports "no upstream
path from any source". Feed sinks from a streamlet.

Round-trip note: prettify emits an inlet and the definition after it on
one line. Two new sinks tripped this; canonical form has to be matched by
hand.

### 2026-08-03: riddlc 2.0.0-rc.9-21-2db8f1d0 — include transparency

Recheck after the upgrade: **187 models, 0 errors, 0 nonzero exits, round
trip 187/187, `.bast` unchanged** (BAST format stable since revision 3).

`c98e33e5e` let the AST content accessors see through `include` files.
Every entity in this corpus lives in an include, so two context-level
completeness checks that key off `c.entities` had been **dormant for the
whole corpus** and are now live — 6 new `[completeness]` warnings, the
only findings anywhere:

- **4 × tell-dispatch on split/merge/flow.** The check requires every
  streamlet with inlets and handlers to `tell` an entity. Right for a
  `sink` — that is the boundary that dispatches inward, and every sink in
  the corpus already does it — but wrong for split/merge/flow, which
  route between ports by definition. No honest edit satisfies it.
- **2 × "context has entities but no Sink streamlet"** (`Delivery`,
  `Inventory`). 185 of ~190 contexts satisfy this, so the convention is
  real. `Delivery` is a genuine gap: the `ToDelivery` adaptor tells
  straight into the entity, past any boundary. `Inventory` has no inbound
  stream at all — the app connects directly to the entity's own inlet,
  which the check does not count. Fixing `Inventory` would mean modelling
  a replenishment flow from Corporate, a cross-domain addition left for
  Reid's call.

Filed as
`../riddl/task/include-transparency-activated-two-dormant-checks.md`.

Note for whoever adds those sinks: a sink handling `on command X` where X
declares `yields` hits the relay problem. The corpus's working sinks
handle an **event** and tell a **command**, which sidesteps it.

## Completed Work

### 2026-05-18: Complete Handlers + Sync Docs to riddlc 1.23.0

Two cohesive commits on `main`:

1. **`dea0645` — Update CLAUDE.md to reflect current build versions**
   - Bumped `riddlc` / `sbt-riddl` from 1.17.1 → 1.23.0 (per
     `project/plugins.sbt`)
   - Bumped `sbt-ossuminc` from 1.3.5 → 1.4.0
   - Removed stale `riddl-lib` row (no longer a build dep)
   - Corrected three references that incorrectly claimed
     validation was wired into `sbt compile`; clarified that
     `validateOnCompile = false` and validation must be run
     explicitly via `sbt v`
   - Bumped "canonical form as of riddlc 1.16.5 prettify" →
     `1.23.0` after verifying byte-identical prettify output
     on `commerce/e-commerce/shopping-cart`

2. **`079f231` — Complete handler implementations + regenerate
   .bast across all 187 models** (501 files, +14074/−1408)
   - Replaced placeholder `prompt "..."` stubs in adaptor and
     repository handlers with concrete messaging:
     `tell command X to entity Y`, `tell event X to entity Y`
   - Added missing commands, queries, and results to entities
     (e.g. `InitializeCart`, `GetCart`, `CartResult` on `Cart`)
   - All 187 models pass `sbt riddlcValidate` against 1.23.0
   - `.bast` files regenerated via `sbt riddlcBastify`

### 2026-02-21: Upgrade to riddlc 1.13.1 + sbt-riddl + Prettify

Upgraded from riddlc 1.10.2 to 1.13.1 and adopted the sbt-riddl
plugin, replacing custom `project/RiddlcTasks.scala`. Reformatted
all 187 models using `riddlc prettify`.

**Changes:**

1. **sbt-riddl plugin** — Added `com.ossuminc:sbt-riddl:1.13.1`
   to `project/plugins.sbt`. Provides `riddlcValidate`,
   `riddlcBastify`, `riddlcPrettify`, `riddlcParse`, `riddlcInfo`.
   Replaces all custom task implementations.

2. **Simplified build.sbt** — Removed custom task keys and
   `RiddlcTasks` wiring. Plugin configured with:
   - `riddlcSourceDir := baseDirectory.value` (scan repo root)
   - `riddlcConfExclusions := Seq("patterns")`
   - `riddlcValidateOnCompile := true`
   - Command aliases: `v`, `b`, `r`

3. **Deleted `project/RiddlcTasks.scala`** — All functionality
   now provided by the plugin.

4. **Reformatted all 187 models** — `sbt riddlcPrettify` applied
   canonical RIDDL syntax:
   - `fieldName: Type` (colon syntax, was `fieldName is Type`)
   - `Type?` (postfix optional, was `optional Type`)
   - `described as { |text }` (markdown, was `described by "text"`)
   - `on command X is {` (added `is` keyword)
   - No commas between aggregate fields
   - Consistent indentation and blank line separation

5. **Removed .bast files** — 187 `.bast` files deleted from
   tracking. They had already been deleted in working tree since
   1.10.2; this commit makes it official. Regenerate with `sbt b`.

6. **Prettify bug reporting** — Filed and resolved three bugs
   during the upgrade process (1.12.0–1.12.3):
   - Commas inserted between fields (fixed 1.12.1)
   - `} with {` split across lines (fixed 1.12.1)
   - Include paths not relative to containing file (fixed 1.12.3)
   - ANSI codes in version check (fixed 1.13.1)

### 2026-02-15: Upgrade to riddlc 1.10.2 + Full Round-Trip Verified

Upgraded from riddlc 1.8.2 through 1.10.0 → 1.10.1 → 1.10.2,
driving unbastify bug fixes through two bug reports.

**Changes:**

1. **riddlc 1.10.0** — Updated from 1.8.2. All 187 models validate.
   Unbastify had 13 critical syntax violations (0/187 pass
   round-trip). Filed `../riddl/unbastify-bug-report.md`.

2. **riddlc 1.10.1** — Fixed the 13 syntax violations. 182/187 pass
   unbastify+re-parse. 5 models still fail (missing `|` on markdown
   lines, `on other` → `on pther` corruption). All 187 fail binary
   comparison due to include structure loss (expected). Filed
   `../riddl/unbastify-bug-report-1.10.1.md`.

3. **riddlc 1.10.2** — Fixed remaining parse errors. **187/187 pass
   all three round-trip checks** (unbastify, binary comparison,
   prettify+flatten source diff).

4. **Round-trip verification script** — Created and iteratively
   refined `scripts/verify-bast-roundtrip.sh`. Key design decisions:
   - Check 2 flattens original via `prettify --single-file` before
     bastifying, so both .bast files come from single-file sources
     (apples-to-apples comparison, avoids include structure delta)
   - Both files bastified from the same directory path to avoid
     .bast embedded-path differences
   - Check 3 compares both .riddl text and .bast output from
     prettified sources

5. **Regenerated all 187 .bast files** in 1.10.2 format.

### 2026-02-13: Update to riddlc 1.8.2 + BAST Generation

Upgraded from riddlc 1.8.0 to 1.8.2 and added `sbt bastify` command
to generate Binary AST (.bast) files for all models.

**Changes:**

1. **Build refactor** — Extracted task implementations from `build.sbt`
   to `project/RiddlcTasks.scala` (Scala 2.12). `build.sbt` now
   declares task keys and wires them to `RiddlcTasks` methods.

2. **riddlc 1.8.2 upgrade** — Updated `riddlVersion` from `1.8.0` to
   `1.8.2`. All 187 models validate cleanly (no new warnings).

3. **bastify task** — Added `riddlcBastifyAll` task with aliases
   `bastify` and `b`. Extracts `input-file` from each model's `.conf`
   and runs `riddlc bastify <file>`. Generated 187 .bast files (~4s).

4. **Round-trip verification** — Spot-checked 7 models with
   `riddlc unbastify`. 5/7 deserialized successfully but unbastified
   output has known limitations (riddlc 1.8.2 bug). BAST generation
   itself is reliable.

5. **Bug report** — Wrote detailed `unbastify-bug-report.md`
   documenting two distinct bugs (deserialization crash on 2 models,
   lossy round-trip on others) with full reproduction steps, failing
   model analysis, and structural feature inventory. Moved to
   `../riddl/unbastify-bug-report.md` for the riddl team.

### 2026-02-12: Fix All riddlc 1.8.0 Amber Warnings

Upgraded from riddlc 1.7.0 to 1.8.0 and resolved all ~1760 amber-level
warnings across 180 models (630 files changed, 2950 insertions, 1729
deletions).

**Three categories of warnings resolved:**

1. **Field overloading (~1700 warnings)** — Same field name used with
   different types within a context scope. Fixed by renaming fields
   with semantic prefixes:
   - `status` → `orderStatus`, `paymentStatus`, `seasonStatus`, etc.
   - `amount` → `paymentAmount`, `refundAmount`, `captureAmount`, etc.
   - `reason` → `cancellationReason`, `holdReason`, etc.
   - `endDate`/`startDate` → `filterEndDate`, `campaignEndDate`, etc.
   - Optional vs non-optional conflicts → `updatedCompletedAt`,
     `currentBooking`, `assignedDriver`, etc.
   - `many T` vs `many optional T` → `scheduledMatches`, etc.

2. **Repository handlers (~30 warnings)** — Repositories had
   `on event Entity.EventCreated` which should be
   `on command Entity.CreateEntity` (repositories handle commands).

3. **Adaptor handlers (~30 warnings)** — "to" adaptors referenced
   source entity events instead of target context commands (e.g.
   `on event Cart.CartCheckedOut` →
   `on command OrderService.CreateOrder`).

Also updated build.sbt to unify `riddlLibVersion`/`riddlcVersion`
into single `riddlVersion = "1.8.0"`.

**Process:** Used a Python script for mechanical repository handler
fixes across 157 models, then 10 parallel Claude agents to fix
remaining field overloading, adaptor, and edge-case warnings across
all 20 sectors. Final validation sweep confirmed 186/186 pass.

### 2026-02-11: NAICS Codes + sbt Validation Integration

**Task 1: NAICS Codes in all READMEs**

Added `## NAICS Code` section to all 186 model READMEs with the
closest NAICS industry classification code. The repository uses BLS
sector/subsector decomposition which doesn't perfectly map to NAICS,
so codes are approximate best-fit matches (4-6 digit codes).

- 157 existing READMEs updated with NAICS code sections
- 29 missing READMEs created from scratch (read .riddl files to
  derive content, included NAICS codes)
- NAICS codes sourced from naics.com and census.gov references

**Task 2: sbt compile validates all RIDDL models**

Rewrote `build.sbt` to integrate riddlc validation into the build:

- `downloadRiddlc` task: Downloads and caches riddlc binary from
  GitHub releases (platform-aware: macOS ARM64, Linux x86_64, or
  JVM universal). Cached in `.riddlc/{version}/bin/riddlc`.
- `riddlcValidateAll` task: Finds all 186 `.conf` files and runs
  `riddlc from <conf> validate` on each. Reports failures with
  error details.
- Wired into `Compile / compile` so `sbt compile` triggers
  validation automatically.
- Command aliases: `sbt validate` and `sbt v`.
- All 186 models pass with riddlc 1.7.0 in ~6 seconds.

Research notes:
- Evaluated sbt-riddl plugin (exists in riddl repo) — functional
  but only handles one `.conf` per project, not suitable for 186.
- riddlc 1.7.0 native binaries available (~4MB macOS ARM64 zip).
- Zip structure uses `bin/riddlc` (not root-level binary).
- Added `.riddlc/` to `.gitignore`.

### 2026-02-04: Fixed ALL Validation Errors (45 Models)

Previously 45/186 models failed `riddlc validate`. All now pass with 0 errors.

**Fixes by category:**

1. **briefly/described outside with{}** (4 models) - Wrapped in `with {}`
   blocks for author, user, epic, case, domain, context, entity definitions

2. **Ambiguous path references** (25 models) - Renamed epic cases with
   UseCase suffix, renamed conflicting enum values with Status/Role/Outcome
   suffix, fully qualified cross-context command references

3. **Unresolved EmailAddress** (8 models) - Added `type EmailAddress is
   String(5, 254)` to models that referenced it

4. **Unresolved Year type** (5 models) - Added `type Year is Integer`

5. **Decimal fractional part** (3 models) - Changed `Decimal(x, 0)` to
   `Decimal(x, 2)` for positive fractional part

6. **Complex multi-error models** (4 models) - fund-accounting,
   warehouse-management, prescription-management, case-management required
   structural changes: projector records, state definitions, handler syntax,
   outlet removal, step syntax fixes

**Key patterns discovered:**
- Epic cases cannot share names with entity commands
- Enum values cannot share names with events/commands/users
- `on command X` cannot use qualified paths like `Entity.Command`
- `outlet` is only valid in streamlets, not entities/contexts
- Bare strings invalid in handlers; use comments instead
- `wants to "..."` should be `wants "to ..."`

### 2026-02-04: Fixed Author Emails (57 models)

Audited all models for incorrect `support@ossum.ai` email. Found 57
early models (commerce, construction, education, engineering,
entertainment, finance, government, healthcare, hospitality, insurance,
logistics, manufacturing, technology, transportation sectors). Fixed
all to `support@ossuminc.com`.

### 2026-02-04: Generated Final Model (design-review)

Generated `engineering/project-engineering/design-review` -- the last
remaining model (175 of 175). Covers submittal management, review
assignment/routing, comment collection and resolution, revision tracking,
approval workflow, and design milestone sign-off. Validated with riddlc
(0 errors, only expected usage warnings for external contexts).

### 2026-02-03: Session Recovery - Committed 32 Crash-Orphaned Models

Previous session crashed after generating 32 models that were never
committed. This session recovered those models by:
1. Scanning all leaf directories for README-only (incomplete) models
2. Discovering all 32 were actually generated on disk but uncommitted
3. Committing all 32 in a single recovery commit
4. Found 1 previously-untracked incomplete model:
   `engineering/project-engineering/design-review` (README only)

### 2026-02-03: Continued Model Generation (55 New Models)

Continued systematic generation, achieving major progress from 85 to 140 models:

**Manufacturing Sector (10 models):**
- `discrete/assembly-operations` - Assembly line operations
- `discrete/bill-of-materials` - BOM management
- `machining/cnc-operations` - CNC machine operations
- `machining/precision-manufacturing` - Precision part production
- `maintenance/equipment-maintenance` - Equipment maintenance
- `maintenance/asset-lifecycle` - Asset lifecycle management
- `process/batch-processing` - Batch production
- `process/quality-control` - Quality inspection
- `textiles/apparel-manufacturing` - Apparel production
- `textiles/fabric-production` - Fabric manufacturing

**Healthcare Sector (11 models):**
- `hospitals/admission-discharge` - ADT workflow
- `hospitals/lab-orders` - Laboratory orders
- `hospitals/nursing-workflow` - Nursing documentation
- `hospitals/operating-room` - OR scheduling
- `hospitals/radiology-workflow` - Radiology operations
- `hospitals/supply-chain` - Hospital supply chain
- `life-sciences/clinical-trials` - Trial management
- `life-sciences/drug-supply-chain` - Pharma distribution
- `payer/member-enrollment` - Member enrollment
- `pharmacy/medication-dispensing` - Dispensing workflow
- `pharmacy/prescription-management` - Prescription processing

**Insurance Sector (4 models):**
- `property-casualty/claims-processing` - Claims workflow
- `property-casualty/policy-administration` - Policy admin
- `life-annuity/policy-lifecycle` - Life policy management
- `reinsurance/treaty-management` - Treaty management

**Technology Sector (5 models):**
- `devops/deployment-pipeline` - Deployment automation
- `devops/incident-management` - Incident response
- `platform/api-management` - API gateway
- `platform/identity-management` - IAM
- `saas/customer-success` - Customer success

**Entertainment Sector (2 models):**
- `live-events/ticket-sales` - Ticket sales
- `sports/team-management` - Sports team operations

**Investment Sector (3 models):**
- `asset-management/fund-accounting` - Fund accounting
- `private-equity/portfolio-management` - Portfolio management
- `venture-capital/fund-management` - VC fund operations

**Logistics Sector (3 models):**
- `warehousing/warehouse-management` - Warehouse operations
- `supply-chain/order-fulfillment` - Order fulfillment
- `fulfillment/returns-processing` - Returns processing

**Marketing Sector (2 models):**
- `campaigns/campaign-management` - Campaign management
- `analytics/marketing-analytics` - Marketing analytics
- `advertising/ad-serving` - Digital ad serving

**Professional Services (2 models):**
- `legal/case-management` - Legal case management
- `accounting/client-accounting` - Client accounting
- `hr-services/payroll-processing` - Payroll processing

**Telecommunications Sector (3 models):**
- `billing/usage-billing` - Usage billing
- `network/service-provisioning` - Service provisioning
- `customer/subscriber-management` - Subscriber management

**Natural Resources (3 models):**
- `mining/mine-operations` - Mine operations
- `oil-gas/well-management` - Oil/gas well lifecycle
- `agriculture/crop-management` - Crop production
- `forestry/timber-management` - Timber operations

**Utilities Sector (3 models):**
- `electric/grid-operations` - Grid operations
- `water/water-distribution` - Water distribution
- `gas/gas-distribution` - Gas distribution
- `metering/smart-metering` - AMI smart metering

### 2026-02-02: Continued Model Generation (68 Models)

Continued systematic generation across multiple sectors:

**Government Sector (7 models):**
- `regulatory/licensing` - Professional/business license management
- `public-safety/emergency-dispatch` - 911 emergency dispatch
- `public-safety/records-management` - Law enforcement records
- `citizen-services/case-management` - Citizen service requests
- `citizen-services/benefits-administration` - Benefits programs
- `citizen-services/permit-management` - Building permits

**Professional Services (1 model):**
- `accounting/client-accounting` - Accounting engagement management

**Technology Sector (4 models):**
- `saas/usage-metering` - SaaS usage tracking and billing
- `saas/subscription-management` - Subscription lifecycle
- `saas/tenant-provisioning` - Multi-tenant provisioning
- `devops/ci-cd-pipeline` - CI/CD pipeline orchestration
- `devops/infrastructure-as-code` - IaC deployment
- `devops/observability` - Monitoring and alerting

**Finance Sector (9 models):**
- `banking/account-management` - Bank account operations
- `banking/loan-origination` - Loan application processing
- `banking/credit-decisioning` - Credit risk evaluation
- `payments/payment-processing` - Payment transactions
- `payments/merchant-acquiring` - Merchant onboarding
- `payments/digital-wallet` - Digital wallet operations
- `payments/fund-transfer` - Money transfers
- `trading/order-management` - Trading order execution
- `trading/trade-settlement` - Trade settlement

**Healthcare Sector (5 models):**
- `hospitals/patient-registration` - Patient intake
- `hospitals/appointment-scheduling` - Appointment management
- `clinical/clinical-encounter` - Clinical documentation
- `clinical/care-coordination` - Care team coordination
- `payer/claims-adjudication` - Claims processing

**Insurance Sector (2 models):**
- `property-casualty/policy-management` - P&C policy lifecycle
- `property-casualty/claims-adjudication` - Claims processing

**Manufacturing Sector (2 models):**
- `maintenance/work-order-management` - Work order processing
- `discrete/inventory-management` - Inventory tracking

**Transportation Sector (11 models):**
- `passenger/ride-sharing` - Ride-sharing operations
- `passenger/airline-reservations` - Flight bookings
- `passenger/transit-operations` - Public transit
- `freight/freight-forwarding` - Freight logistics
- `freight/intermodal` - Intermodal transport
- `freight/customs-brokerage` - Customs clearance
- `fleet/fleet-management` - Fleet operations
- `fleet/route-optimization` - Route planning
- `maritime/port-operations` - Port logistics
- `maritime/vessel-management` - Vessel tracking

**Hospitality Sector (8 models):**
- `lodging/hotel-reservations` - Hotel bookings
- `lodging/guest-services` - Guest management
- `lodging/property-management` - Property operations
- `food-service/restaurant-operations` - Restaurant management
- `food-service/catering-management` - Catering services
- `travel/tour-operations` - Tour packages
- `travel/car-rental` - Vehicle rentals
- `events/venue-management` - Venue operations
- `events/event-registration` - Event ticketing

**Entertainment Sector (5 models):**
- `media/content-management` - Media content
- `media/streaming-platform` - Streaming services
- `gaming/matchmaking` - Game matchmaking
- `gaming/game-economy` - Virtual economies
- `marketing/advertising-delivery` - Ad serving

**Education Sector (6 models):**
- `academic/course-management` - Course catalog
- `academic/learning-management` - LMS
- `academic/student-information` - Student records
- `certification/credentialing` - Certification tracking
- `corporate-training/competency-management` - Skills tracking
- `corporate-training/training-administration` - Training programs

**Engineering Sector (6 models):**
- `consulting/engagement-management` - Consulting engagements
- `consulting/knowledge-management` - Knowledge base
- `product-development/plm-integration` - PLM systems
- `product-development/prototype-management` - Prototyping
- `product-development/design-review` - Design reviews
- `project-engineering/engineering-project` - Engineering projects

**Investment Sector (1 model):**
- `venture-capital/deal-flow` - Deal pipeline management

### 2026-02-01: Commerce & Construction Sectors (17 Models)

Completed all models for the first two sectors:

**Commerce Sector (10 models):**
- `e-commerce/order-management` - Order lifecycle with fulfillment saga
- `e-commerce/product-catalog` - Product catalog with categories
- `e-commerce/shopping-cart` - Cart management and checkout
- `marketplace/vendor-management` - Vendor onboarding
- `marketplace/order-orchestration` - Multi-vendor orders
- `retail/inventory-management` - Stock tracking
- `retail/point-of-sale` - POS transactions
- `retail/store-operations` - Store management
- `wholesale/distribution` - Wholesale distribution
- `wholesale/trade-credit` - Credit management

**Construction Sector (7 models):**
- `field-operations/equipment-tracking` - Equipment lifecycle
- `field-operations/job-site-management` - Site operations
- `project-management/bid-management` - Bid processing
- `project-management/construction-project` - Project tracking
- `project-management/subcontractor-management` - Subcontractor relations
- `real-estate/property-management` - Property leasing
- `real-estate/transaction-management` - Real estate transactions

---

## Active Work

### Pending: Upgrade sbt-riddl to 1.13.2

The sbt-riddl plugin has a fix in progress (in the `riddl` repo) to
eliminate the `InterruptedException` stack trace that appears when
running `riddlcValidate` or `riddlcBastify`. The fix replaces
`.!(logger)` with `ProcessIO(_.close(), ...)` to avoid piping stdin
to riddlc subprocesses. This will ship as riddlc/sbt-riddl 1.13.2.
Once published, update `project/plugins.sbt` to use the new version.

### Sector Completion Status

All 20 sectors complete (186 models total):

| Sector | Models |
|--------|--------|
| commerce | 10 |
| construction | 7 |
| education | 6 |
| engineering | 7 |
| entertainment | 11 |
| finance | 9 |
| government | 7 |
| healthcare | 16 |
| hospitality | 11 |
| insurance | 5 |
| investment | 9 |
| logistics | 11 |
| manufacturing | 11 |
| marketing | 11 |
| natural-resources | 10 |
| professional-services | 8 |
| technology | 12 |
| telecommunications | 9 |
| transportation | 9 |
| utilities | 7 |

---

## Design Decisions

### Model File Structure (2026-02-01)

Each model uses 6 files:
- `model.conf` - riddlc configuration pointing to main file
- `model.riddl` - Domain definition with includes
- `types.riddl` - Shared type definitions
- `Entity.riddl` - One file per entity
- `Context.riddl` - Main bounded context with repository/projector
- `external-contexts.riddl` - External systems, `external context X is {`
  (this entry said `option is external` until 2026-08-05; that form has
  zero occurrences and is not RIDDL 2.0 syntax)

### RIDDL Syntax Notes (2026-02-04)

Important syntax findings during validation fix work:
- `briefly`/`described by` must be inside `with {}` blocks
- Epic cases cannot share names with entity commands (use UseCase suffix)
- Enum values cannot share names with events/commands/users
- `on command X` cannot use qualified paths (no `Entity.Command`)
- `outlet` only valid in streamlets, not entities/contexts
- Bare strings invalid in handlers; use comments or `???`
- `wants to "..."` should be `wants "to ..."`
- `Decimal(x, y)` requires y > 0 (positive fractional part)
- State syntax: `state X of TypeName with {}` (no `is {}` body)
- Handlers belong at entity level, not nested in states

### Author Block Pattern (2026-02-02)

Standard author block for all models:
```riddl
author OssumInc is {
  name is "Ossum Inc."
  email is "support@ossuminc.com"
}
```

---

## Blockers

- **None currently**

---

## Notes

- riddlc: auto-downloaded by sbt-riddl plugin to `~/.cache/riddlc/`
- Also available via Homebrew or staged build
- riddlc 1.13.1 validates all 187 models in ~8 seconds
- `sbt r` reformats all 187 models in ~6 seconds
- `./scripts/verify-bast-roundtrip.sh` — round-trip verification
- Reference model: `finance/banking/account-management/`
- Build integration via `com.ossuminc:sbt-riddl` plugin
