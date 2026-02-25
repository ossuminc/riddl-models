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

**Date**: 2026-02-21
**Phase**: riddlc 1.13.1 — sbt-riddl Plugin + Prettified Models

- **187 models** validated with riddlc 1.13.1 — zero errors
- All models reformatted via `riddlc prettify` to canonical syntax
  (colon fields, `Type?` optionals, `described as` markdown,
  `is` on handlers, no commas between fields)
- Build uses **sbt-riddl plugin** (replaced custom RiddlcTasks.scala)
- `.bast` files removed from tracking (regenerate with `sbt b`)
- All model READMEs have NAICS codes
- `sbt compile` auto-downloads riddlc and validates all models

---

## Completed Work

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

No active work items. All 187 models pass riddlc 1.13.1 validation
and have been reformatted to canonical RIDDL syntax.

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
