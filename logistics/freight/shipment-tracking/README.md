# Shipment Tracking

Freight shipment visibility, location tracking, and delivery confirmation.

## NAICS Code

**488510** - Freight Transportation Arrangement

## Scope

This model covers shipment tracking operations, including:

- Shipment booking and pickup recording
- Real-time location and milestone tracking
- ETA calculation and delivery window updates
- Delivery confirmation with proof of delivery
- Exception reporting and resolution
- Return initiation and processing

## Key Concepts

| Concept | Description |
|---------|-------------|
| Shipment | A freight movement from shipper to consignee |
| TrackingEvent | A scan or milestone in the shipment journey |
| DeliveryWindow | Estimated delivery time range |
| ExceptionInfo | A delivery exception requiring resolution |

## Related Patterns

- `patterns/entity/event-sourced/` - For shipment tracking history
- `patterns/projection/read-model/` - For delivery analytics dashboards
