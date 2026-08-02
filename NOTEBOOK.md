# NOTEBOOK.md - riddl-models

Development journal for active work on the riddl-models repository.

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

**6 of 13 entities converted**: `InventoryItem`, `Shift`, `Campaign`,
`MenuItem`, `MenuRelease`, `PurchaseOrder`. Model validates clean, round
trip 48/48.

**The other 7 are blocked**, and not by anything in the model.
`checkYieldConformance` has no exemption for a clause that *refuses* a
command, so a state that rejects `AddItem` is required to `yield event
ItemAdded` — to record the change it just declined. The restaurant
aggregates are all multi-state: 52 of 78 commands have more than one
clause, and 268 refusing clauses would each be forced to yield a success
event. Filed as
`../riddl/task/yields-conformance-forces-refusing-clauses-to-yield.md`.

Corpus state under this binary: **194 errors, 27 deprecations in 10
models** — those already carrying `option event-sourced()`. All of them
are single-clause, so the recipe applies unchanged; that work is next and
is not blocked. Every `.bast` is stale (FORMAT_REVISION 2 → 3).

### Open Loose Ends

- 8 untracked helper scripts at repo root and in `scripts/`
  (`fix-models.py`, `fix_models.py` near-duplicate, etc.) —
  triage needed: keep the useful ones in `scripts/`, delete
  scratch work at the root

---

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
- `external-contexts.riddl` - External systems with `option is external`

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
