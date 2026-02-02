# NOTEBOOK.md - riddl-models

Development journal for active work on the riddl-models repository.

---

## Current Status

**Date**: 2026-02-01
**Phase**: Model Generation - First Model Complete

Successfully created and validated the first domain model (order-management)
as a proof of concept. The model compiles cleanly with riddlc, demonstrating
correct RIDDL syntax patterns for the remaining 155 models.

**Validation**: Use `riddlc from <config>.conf validate` for all models.

---

## Completed Work

### 2026-02-01: Order Management Model (Proof of Concept)

Created complete order-management model at `commerce/e-commerce/order-management/`:

**Files created:**
- `order-management.conf` - riddlc configuration
- `order-management.riddl` - Domain entry point with author, users, epics
- `types.riddl` - Shared types (OrderId, Money, Address, PaymentMethod, etc.)
- `Order.riddl` - Order entity with 5 states, commands, events, handler
- `Shipment.riddl` - Shipment tracking entity with 3 states
- `Return.riddl` - Return/refund entity with 5 states
- `OrderFulfillmentSaga.riddl` - 4-step saga with compensation
- `OrderContext.riddl` - Main context with adaptors, repository, projector
- `external-contexts.riddl` - 4 external contexts (PaymentGateway, etc.)

**Key learnings documented in CLAUDE.md:**
- `described by` syntax: use quoted strings OR multi-line with `}` on own line
- Naming collisions: enum values vs state names need different names
- External contexts: use `option is external` in `with` block
- Messaging: `tell event/command X to entity Y`
- State transitions: `morph entity X to state Y with command Z`

**Validation result:** 0 errors, only informational warnings for:
- Missing metadata on some fields (external-contexts.riddl, epic steps)
- Unused types (RefundStatus, ReturnStatus, DailyOrderMetrics)

### 2026-02-01: MCP Server Configuration

- Tested RIDDL comprehension with vending machine example
- Identified gaps: missing `with` metadata syntax, other constructs
- Created `.mcp.json` for local riddl-mcp server at `localhost:8080/mcp/v1`
- Server provides RIDDL syntax guidance and validation tools

### 2026-02-01: Complete README Documentation

- Added README.md files to all 156 model directories
- Each README includes: scope, key concepts table, related patterns
- Committed in 3 cohesive groups:
  1. Project configuration (CLAUDE.md, build.sbt, etc.)
  2. Patterns and schemas (27 files)
  3. Domain model ontology (246 files)
- Updated .gitignore to exclude .idea/, .bsp/, target/
- Pushed all commits to origin/main

### 2026-01-29: Repository Structure Setup

- Created CLAUDE.md with project documentation
- Created NOTEBOOK.md (this file)
- Enhanced README.md with project overview
- Created 18 top-level sector directories with READMEs
- Created patterns/ directory with 5 pattern categories
- Created schemas/ directory with model-metadata.schema.json
- Created build.sbt with RIDDL validation infrastructure
- Created RiddlValidationTest that validates all .riddl files on `sbt test`

---

## Active Work

### In Progress: Commit Order Management Model

Files to commit in cohesive batches:
1. Configuration and entry point files
2. Type definitions and entity files
3. Context and external system files

---

## Next Steps

1. **Commit Order Management Model** (in progress)
   - Batch commits for the 10 new files

2. **Generate Remaining Models**
   - Use order-management as template
   - Work through sectors systematically
   - Validate each with riddlc before committing

3. **Fix Pattern Example Files**
   - Update with correct syntax
   - Validate all examples pass `sbt test`

4. **CI Integration**
   - Add GitHub Actions workflow for validation
   - Ensure PRs must pass validation

---

## Design Decisions

### Model File Structure (2026-02-01)

Each model should be broken into separate files:
- `model.conf` - riddlc configuration pointing to main file
- `model.riddl` - Domain definition with includes
- `types.riddl` - Shared type definitions
- `*.riddl` - One file per entity/saga
- `Context.riddl` - Main bounded context with adaptors
- `external-contexts.riddl` - External systems with `option is external`

This structure improves readability and allows focused editing.

### Validation Approach (2026-01-29)

Used test-based validation rather than custom sbt task because:
- sbt build definitions use Scala 2.12, can't easily use riddl-lib
- ScalaTest provides clear per-file test results
- Works with standard `sbt test` workflow
- Template files are automatically skipped via placeholder detection

### Directory Structure (2026-01-29)

- 18 top-level sectors based on NAICS alignment
- 3-level hierarchy: sector → subsector → model
- Each sector has README.md explaining scope
- Complexity tiers (starter/standard/enterprise) via metadata

---

## Blockers

- **None currently**

---

## Notes

- sbt uses Scala 2.12 for build definitions (documented in ossuminc/CLAUDE.md)
- Project source code uses Scala 3.3.7 with `-new-syntax` flag
- Use `given`/`then`/`end` syntax in test files, not Scala 2 style
- riddlc path: `riddl/riddlc/jvm/target/universal/stage/bin/riddlc`
