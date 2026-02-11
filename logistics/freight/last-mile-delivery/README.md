# Last Mile Delivery

Final delivery operations, route optimization, and proof of delivery.

## NAICS Code

**492110** - Couriers and Express Delivery Services

## Scope

This model covers last mile delivery operations, including:

- Delivery creation and route assignment
- Driver dispatch and ETA tracking
- Delivery attempt recording and rescheduling
- Proof of delivery (signature, photo)
- Failed delivery handling and return to sender
- Daily delivery analytics

## Key Concepts

| Concept | Description |
|---------|-------------|
| Delivery | A package delivery to a customer address |
| Route | An optimized sequence of delivery stops |
| DeliveryAttempt | A single attempt to deliver a package |
| ProofOfDelivery | Evidence of successful delivery |

## Related Patterns

- `patterns/workflow/process-manager/` - For delivery route execution
- `patterns/entity/event-sourced/` - For delivery attempt history
