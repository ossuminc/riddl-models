# NOTEBOOK.md - riddl-models

Development journal for active work on the riddl-models repository.

---

## Current Status

**Date**: 2026-02-01
**Phase**: Documentation Complete - RIDDL Content Blocked

The repository structure, validation infrastructure, and all README documentation
are complete and pushed to origin. **RIDDL content work remains blocked** waiting
for the improved EBNF grammar and riddlc validation.

Summary of structure:
- 20 sector directories with READMEs
- 70 subsector directories with READMEs
- 156 model directories with READMEs
- 27 pattern template files with documentation
- Validation test infrastructure ready

---

## Completed Work

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

### Validation Infrastructure

The build now includes:
- `sbt test` / `sbt validate` - Validates all RIDDL files
- Template files with `{Placeholders}` are automatically skipped
- Uses riddl-lib 1.1.1 for validation
- Catches syntax and semantic errors

---

## Active Work

### BLOCKED: Fix Pattern RIDDL Files

The pattern example files have RIDDL syntax errors and need to be fixed.
**Waiting for**: EBNF grammar update being done in another thread.

Files to fix:
- `patterns/entity/event-sourced/example.riddl`
- `patterns/entity/aggregate-root/example.riddl`
- `patterns/saga/distributed-transaction/example.riddl`
- `patterns/projection/read-model/example.riddl`
- `patterns/workflow/process-manager/example.riddl`

---

## Next Steps

**All content work blocked on EBNF grammar completion.**

Once unblocked:

1. **Fix Pattern Example Files**
   - Update examples with correct RIDDL syntax
   - Validate all examples pass `sbt test`

2. **Create Real Domain Models**
   - Write complete, validated RIDDL models (not placeholders)
   - Start with commerce/e-commerce/shopping-cart as reference example
   - Each model must validate with riddlc before committing

3. **CI Integration**
   - Add GitHub Actions workflow for validation
   - Ensure PRs must pass validation

---

## Design Decisions

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

- **EBNF Grammar Update**: All RIDDL content (patterns and domain models) requires
  the improved EBNF grammar to be complete. Models must validate with riddlc -
  we don't want placeholder content, only real validated models. Work is being
  done in a separate session. (2026-01-30: Delayed due to Scala compiler issues.)

---

## Notes

- sbt uses Scala 2.12 for build definitions (documented in ossuminc/CLAUDE.md)
- Project source code uses Scala 3.3.7 with `-new-syntax` flag
- Use `given`/`then`/`end` syntax in test files, not Scala 2 style