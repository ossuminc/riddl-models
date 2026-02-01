# Payer

Health insurance operations and claims administration.

## Scope

This subsector covers health plan administration and claims processing,
including:

- Member enrollment and eligibility
- Claims adjudication and payment
- Provider network management
- Utilization management
- Benefits configuration

## Models

| Model | Description |
|-------|-------------|
| `member-enrollment/` | Enrollment, eligibility, and plan selection |
| `claims-adjudication/` | Claim submission, processing, and payment |

## Related Patterns

- `patterns/workflow/process-manager/` - For claims workflows
- `patterns/saga/distributed-transaction/` - For payment processing