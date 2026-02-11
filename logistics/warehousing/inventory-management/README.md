# Inventory Management

Warehouse inventory tracking, stock movements, and replenishment.

## NAICS Code

**493110** - General Warehousing and Storage

## Scope

This model covers inventory management operations, including:

- Inventory initialization and stock receiving
- Stock reservation and allocation for orders
- Picking and location transfers
- Cycle counting and stock adjustments
- Replenishment request generation
- Lot tracking and stock level monitoring

## Key Concepts

| Concept | Description |
|---------|-------------|
| Inventory | A tracked stock item at a warehouse location |
| StockLevel | On-hand, reserved, and available quantities |
| StockMovement | A receipt, pick, transfer, or adjustment |
| ReservationInfo | Stock held for a pending order |

## Related Patterns

- `patterns/entity/event-sourced/` - For inventory movement history
- `patterns/projection/read-model/` - For stock level dashboards
