# Property & Casualty Insurance

General insurance for property, liability, and auto coverage.

## Scope

This subsector covers insurance products that protect against property damage
and liability, including:

- Policy quoting and issuance
- Premium calculation and rating
- Claims intake and investigation
- Loss adjustment and settlement
- Underwriting and risk selection

## Models

| Model | Description |
|-------|-------------|
| `policy-administration/` | Policy lifecycle from quote to renewal |
| `claims-processing/` | Claim submission, investigation, and payout |

## Related Patterns

- `patterns/entity/event-sourced/` - For policy version history
- `patterns/saga/distributed-transaction/` - For claims workflows
- `patterns/workflow/process-manager/` - For underwriting decisions