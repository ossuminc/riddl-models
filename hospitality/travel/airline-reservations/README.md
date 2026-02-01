# Airline Reservations

Flight booking, inventory management, and passenger services.

## Scope

This model covers airline reservation operations, including:

- Flight schedule and inventory management
- Seat availability and booking
- Fare classes and pricing rules
- Passenger name records (PNR)
- Ancillary services (upgrades, baggage, meals)

## Key Concepts

| Concept | Description |
|---------|-------------|
| Flight | A scheduled departure with origin, destination, and timing |
| Booking | A passenger reservation on one or more flights |
| PNR | Passenger Name Record containing all booking details |
| Inventory | Available seats by fare class and cabin |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For multi-leg bookings
- `patterns/entity/event-sourced/` - For booking modification history
