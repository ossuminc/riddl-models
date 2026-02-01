# Media Buying

Media planning, purchasing, and trafficking.

## Scope

This model covers media buying operations, including:

- Media plan development
- Budget allocation by channel
- Insertion order management
- Vendor negotiation and purchasing
- Reconciliation and payment

## Key Concepts

| Concept | Description |
|---------|-------------|
| MediaPlan | A strategy for ad placement |
| InsertionOrder | A purchase agreement for ad space |
| Channel | A media outlet (TV, digital, print) |
| Invoice | A vendor bill for media |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For purchase workflows
- `patterns/entity/event-sourced/` - For plan history
