# Insurance

RIDDL models for property & casualty, life & annuity, and reinsurance
operations.

## Subsectors

### property-casualty/
P&C insurance for property, auto, liability coverage.

**Models:**
- `policy-administration/` - Quote, bind, endorse, renew
- `claims-processing/` - FNOL through settlement

### life-annuity/
Life insurance and annuity products.

**Models:**
- `policy-lifecycle/` - Underwriting, in-force management, benefits

### reinsurance/
Reinsurance treaty and facultative operations.

**Models:**
- `treaty-management/` - Placement, cessions, recoveries

## Common Patterns

Insurance models frequently use:
- Multi-state entities for policy lifecycle (draft → active → lapsed)
- Event sourcing for policy version history
- Saga patterns for claims workflows
- Projectors for actuarial reporting

## Domain-Specific Concepts

- **FNOL** - First Notice of Loss (claim intake)
- **Endorsement** - Mid-term policy modification
- **Cession** - Transfer of risk to reinsurer