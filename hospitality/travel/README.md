# Travel

Travel booking, transportation, and tour operations.

## Scope

This subsector covers travel industry operations, including:

- Airline reservation systems
- Car rental and fleet management
- Tour packaging and operations
- Travel agency and OTA platforms
- Loyalty and rewards programs

## Models

| Model | Description |
|-------|-------------|
| `airline-reservations/` | Flight booking, inventory, and pricing |
| `car-rental/` | Vehicle availability and rental agreements |
| `tour-operations/` | Itinerary planning and guide management |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For multi-leg bookings
- `patterns/entity/aggregate-root/` - For itinerary management