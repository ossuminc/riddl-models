# Inventory Control

Cycle counts, adjustments, and inventory transfers.

## NAICS Code

**493110** - General Warehousing and Storage

## Scope

This model covers inventory control operations, including:

- Cycle counting and physical inventory
- Variance investigation and adjustments
- Inventory transfers between locations
- Lot and serial number tracking
- Expiration and hold management

## Key Concepts

| Concept | Description |
|---------|-------------|
| CountTask | A scheduled inventory verification |
| Adjustment | A correction to recorded quantity |
| Transfer | Movement between warehouse locations |
| Hold | A restriction on inventory use |

## Related Patterns

- `patterns/entity/event-sourced/` - For adjustment history
- `patterns/workflow/process-manager/` - For count workflows
