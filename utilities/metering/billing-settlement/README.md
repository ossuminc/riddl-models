# Billing & Settlement

Rate application, invoice generation, and payment processing.

## NAICS Code

**221100** - Electric Power Generation, Transmission and Distribution

## Scope

This model covers utility billing operations, including:

- Rate schedule management
- Usage-based billing calculation
- Invoice generation and delivery
- Payment processing and posting
- Collections and delinquency

## Key Concepts

| Concept | Description |
|---------|-------------|
| RateSchedule | Pricing rules for consumption |
| Invoice | A customer bill for services |
| Payment | A remittance applied to an account |
| Account | A customer billing relationship |

## Related Patterns

- `patterns/entity/event-sourced/` - For billing history
- `patterns/saga/distributed-transaction/` - For payment processing
