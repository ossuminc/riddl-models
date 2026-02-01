# Mineral Tracking

Ore grades, stockpiles, and shipment tracking.

## Scope

This model covers mineral tracking operations, including:

- Grade sampling and assays
- Stockpile management and reconciliation
- Blending and quality control
- Shipment scheduling and documentation
- Custody transfer and invoicing

## Key Concepts

| Concept | Description |
|---------|-------------|
| Stockpile | Accumulated material with grade |
| Assay | Chemical analysis of ore content |
| Shipment | A sold quantity with specifications |
| Reconciliation | Comparison of measured vs. shipped |

## Related Patterns

- `patterns/entity/event-sourced/` - For stockpile history
- `patterns/saga/distributed-transaction/` - For shipment workflows
