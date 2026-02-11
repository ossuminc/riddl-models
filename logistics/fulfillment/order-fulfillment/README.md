# Order Fulfillment

Pick, pack, and ship workflow for customer orders.

## NAICS Code

**493110** - General Warehousing and Storage

## Scope

This model covers order fulfillment operations, including:

- Order allocation and release
- Pick task generation and execution
- Packing and cartonization
- Carrier selection and labeling
- Shipment confirmation and tracking

## Key Concepts

| Concept | Description |
|---------|-------------|
| Order | A customer request to be fulfilled |
| Allocation | Inventory reserved for an order |
| Carton | A packed container for shipment |
| Shipment | A dispatched order with tracking |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For fulfillment workflow
- `patterns/entity/event-sourced/` - For order history
