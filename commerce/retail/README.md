# Retail

Brick-and-mortar retail operations and omnichannel commerce.

## Scope

This subsector covers physical retail store operations and their integration
with digital channels, including:

- Point-of-sale transaction processing
- In-store inventory management
- Store operations and staff scheduling
- Omnichannel order fulfillment (BOPIS, ship-from-store)
- Customer loyalty programs

## Models

| Model | Description |
|-------|-------------|
| `point-of-sale/` | In-store transaction processing and payments |
| `inventory-management/` | Stock levels, replenishment, and transfers |
| `store-operations/` | Staff scheduling, daily operations, and reporting |

## Related Patterns

- `patterns/entity/event-sourced/` - For inventory tracking with audit trail
- `patterns/projection/read-model/` - For real-time stock availability