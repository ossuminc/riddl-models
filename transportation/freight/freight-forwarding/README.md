# Freight Forwarding

Shipment booking, documentation, and cargo tracking.

## NAICS Code

**488510** - Freight Transportation Arrangement

## Scope

This model covers freight forwarding operations, including:

- Booking and rate quotation
- Bill of lading and documentation
- Carrier selection and routing
- Shipment tracking and visibility
- Proof of delivery and invoicing

## Key Concepts

| Concept | Description |
|---------|-------------|
| Shipment | A cargo movement from origin to destination |
| BookingRequest | A customer request for freight transport |
| BillOfLading | The contract of carriage and receipt of goods |
| Milestone | A tracking event in the shipment journey |

## Related Patterns

- `patterns/entity/event-sourced/` - For shipment tracking history
- `patterns/saga/distributed-transaction/` - For booking confirmation
