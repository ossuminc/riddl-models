# NOTEBOOK.md - riddl-models

Development journal for active work on the riddl-models repository.

---

## Current Status

**Date**: 2026-02-01
**Phase**: Model Generation - Sectors 1 & 2 Complete

Progress: **17 of 172 models** completed (10% complete)
- Commerce sector: 10 models - COMPLETE
- Construction sector: 7 models - COMPLETE
- 155 models remaining across 16 sectors

**Validation**: Use `riddlc from <config>.conf validate` for all models.
**riddlc location**: `../riddl/riddlc/jvm/target/universal/stage/bin/riddlc`

---

## Completed Work

### 2026-02-01: Commerce & Construction Sectors (17 Models)

Completed all models for the first two sectors with full validation:

**Commerce Sector (10 models):**
- `e-commerce/order-management` - Order lifecycle with fulfillment saga
- `e-commerce/product-catalog` - Product catalog with categories
- `e-commerce/shopping-cart` - Cart management and checkout
- `marketplace/vendor-management` - Vendor onboarding and management
- `marketplace/order-orchestration` - Multi-vendor order coordination
- `retail/inventory-management` - Stock tracking and replenishment
- `retail/point-of-sale` - POS transactions and cash management
- `retail/store-operations` - Store opening/closing, staff management
- `wholesale/distribution` - Wholesale order distribution
- `wholesale/trade-credit` - Credit accounts and collections

**Construction Sector (7 models):**
- `field-operations/equipment-tracking` - Equipment lifecycle and GPS
- `field-operations/job-site-management` - Daily reports, safety, crews
- `project-management/bid-management` - RFP response and bid evaluation
- `project-management/construction-project` - Project planning and tracking
- `project-management/subcontractor-management` - Subcontractor relationships
- `real-estate/property-management` - Leasing and maintenance
- `real-estate/transaction-management` - Purchase/sale transactions

**Key syntax patterns established:**
- Enumeration values: simple identifiers (no individual `with {}` blocks)
- Handler clauses: `on command X { ... }` (no `is` required in v1.2.1+)
- External contexts: `option is external` in `with` block
- State transitions: `morph entity X to state Y with command Z`
- Entity messaging: `tell event/command X to entity Y`
- Collection syntax: `many optional Type` (not `optional many`)

### 2026-02-01: MCP Server Configuration

- Tested RIDDL comprehension with vending machine example
- Created `.mcp.json` for local riddl-mcp server at `localhost:8080/mcp/v1`
- Server provides RIDDL syntax guidance and validation tools

### 2026-02-01: Complete README Documentation

- Added README.md files to all 156 model directories
- Each README includes: scope, key concepts table, related patterns
- Pushed all commits to origin/main

### 2026-01-29: Repository Structure Setup

- Created CLAUDE.md, NOTEBOOK.md, enhanced README.md
- Created 18 top-level sector directories with READMEs
- Created patterns/ and schemas/ directories
- Created build.sbt with RIDDL validation infrastructure

---

## Active Work

### In Progress: Generate Remaining Domain Models

155 models remaining across 16 sectors. Work through systematically:

| Sector | Subsectors | Models | Status |
|--------|------------|--------|--------|
| commerce | 4 | 10 | COMPLETE |
| construction | 3 | 7 | COMPLETE |
| education | 3 | 6 | pending |
| engineering | 3 | 6 | pending |
| entertainment | 4 | 10 | pending |
| finance | 3 | 9 | pending |
| government | 3 | 7 | pending |
| healthcare | 5 | 16 | pending |
| hospitality | 4 | 12 | pending |
| insurance | 3 | 4 | pending |
| investment | 3 | 6 | pending |
| logistics | 3 | 8 | pending |
| manufacturing | 5 | 14 | pending |
| marketing | 3 | 6 | pending |
| natural-resources | 4 | 8 | pending |
| professional-services | 3 | 6 | pending |
| technology | 3 | 9 | pending |
| telecommunications | 3 | 6 | pending |
| transportation | 4 | 11 | pending |
| utilities | 4 | 8 | pending |

Each model created with:
- `.conf` file for riddlc
- Main `.riddl` domain file
- `types.riddl` for shared types
- Entity file(s) with states and handlers
- `Context.riddl` for bounded context
- `external-contexts.riddl` for integrations

---

## Next Steps

1. **Continue Model Generation**
   - Next sector: education
   - Work through sectors systematically
   - Validate each with riddlc before committing
   - Commit each model separately (not pushed yet)

2. **User Review**
   - User to review all commits before push
   - 17 model commits pending review

3. **CI Integration** (future)
   - Add GitHub Actions workflow for validation
   - Ensure PRs must pass validation

---

## Design Decisions

### Model File Structure (2026-02-01)

Each model broken into separate files:
- `model.conf` - riddlc configuration pointing to main file
- `model.riddl` - Domain definition with includes
- `types.riddl` - Shared type definitions
- `Entity.riddl` - One file per entity
- `Context.riddl` - Main bounded context with adaptors
- `external-contexts.riddl` - External systems with `option is external`

### RIDDL Syntax Notes (2026-02-01)

Important syntax findings during model generation:
- Enum values cannot have individual `with { briefly ... }` blocks
- Handler `on` clauses work with or without `is` in v1.2.1+
- Identifier minimum length is 3 characters (e.g., `VA` → `VALoan`)
- User/enum name collisions trigger warnings (use distinct names)

### Validation Approach (2026-01-29)

Test-based validation using riddlc directly:
- Works with `riddlc from model.conf validate`
- Clear error messages for syntax issues
- Usage warnings are informational (not errors)

---

## Blockers

- **None currently**

---

## Notes

- sbt uses Scala 2.12 for build definitions (documented in ossuminc/CLAUDE.md)
- Project source code uses Scala 3.3.7 with `-new-syntax` flag
- riddlc path: `../riddl/riddlc/jvm/target/universal/stage/bin/riddlc`
- Version 1.2.1+ required for validation
