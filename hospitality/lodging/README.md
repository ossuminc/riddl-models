# Lodging

Hotels, resorts, and accommodation management.

## Scope

This subsector covers hospitality property operations, including:

- Reservation and booking management
- Room inventory and rate management
- Guest check-in and check-out
- Housekeeping and maintenance
- Guest services and amenities

## Models

| Model | Description |
|-------|-------------|
| `reservation-system/` | Booking, availability, and rate management |
| `property-management/` | Room status, housekeeping, and maintenance |
| `guest-services/` | Concierge, amenities, and guest requests |

## Related Patterns

- `patterns/entity/event-sourced/` - For reservation changes
- `patterns/saga/distributed-transaction/` - For booking workflows