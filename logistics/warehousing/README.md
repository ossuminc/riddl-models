# Warehousing

Warehouse operations and inventory management.

## Scope

This subsector covers warehouse and distribution center operations, including:

- Warehouse management systems
- Inventory receiving and putaway
- Pick, pack, and ship
- Cycle counting and audits
- Labor management

## Models

| Model | Description |
|-------|-------------|
| `warehouse-management/` | Locations, inventory, and operations |
| `inventory-control/` | Stock levels, movements, and adjustments |

## Related Patterns

- `patterns/entity/event-sourced/` - For inventory movements
- `patterns/projection/read-model/` - For available-to-promise