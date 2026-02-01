# Usage Rating

CDR mediation, rating, and billing calculation.

## Scope

This model covers usage rating operations, including:

- CDR collection and mediation
- Usage rating and pricing
- Discount and promotion application
- Aggregation and summarization
- Billing system integration

## Key Concepts

| Concept | Description |
|---------|-------------|
| CDR | Call Detail Record with usage data |
| Rating | Application of rates to usage |
| Tariff | Pricing rules and rate tables |
| RatedUsage | Priced usage ready for billing |

## Related Patterns

- `patterns/entity/event-sourced/` - For CDR processing
- `patterns/projection/read-model/` - For usage summaries
