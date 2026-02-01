# Billing

Telecom billing and revenue management.

## Scope

This subsector covers telecom billing operations, including:

- Usage rating and charging
- Invoice generation
- Revenue assurance
- Interconnect billing
- Fraud detection

## Models

| Model | Description |
|-------|-------------|
| `usage-rating/` | CDR processing and charge calculation |
| `revenue-assurance/` | Leakage detection and reconciliation |

## Related Patterns

- `patterns/entity/event-sourced/` - For CDR processing
- `patterns/projection/read-model/` - For revenue dashboards