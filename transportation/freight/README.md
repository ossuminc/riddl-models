# Freight

Freight transportation and cargo logistics.

## Scope

This subsector covers freight and cargo movement, including:

- Freight forwarding and booking
- Intermodal coordination
- Customs brokerage
- Shipment tracking
- Freight audit and payment

## Models

| Model | Description |
|-------|-------------|
| `freight-forwarding/` | Booking, routing, and carrier management |
| `customs-brokerage/` | Import/export documentation and clearance |
| `intermodal/` | Multi-mode shipment coordination |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For multi-leg shipments
- `patterns/entity/event-sourced/` - For shipment tracking