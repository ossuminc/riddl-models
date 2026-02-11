# Warehouse Management

Receiving, putaway, picking, and shipping operations.

## NAICS Code

**493110** - General Warehousing and Storage

## Scope

This model covers warehouse operations, including:

- Inbound receiving and inspection
- Putaway and location management
- Wave planning and picking
- Packing and shipping
- Dock door scheduling

## Key Concepts

| Concept | Description |
|---------|-------------|
| Receipt | Inbound goods processing |
| Location | A defined storage position |
| PickTask | An order to retrieve inventory |
| Shipment | Outbound goods processing |

## Related Patterns

- `patterns/workflow/process-manager/` - For wave processing
- `patterns/entity/event-sourced/` - For inventory movements
