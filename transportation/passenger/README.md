# Passenger

Passenger transportation services.

## Scope

This subsector covers people movement services, including:

- Public transit operations
- Ride-sharing and mobility
- Paratransit and accessible transport
- Fare collection and ticketing
- Schedule and route planning

## Models

| Model | Description |
|-------|-------------|
| `transit-operations/` | Routes, schedules, and vehicle dispatch |
| `ride-sharing/` | Matching, pricing, and driver management |

## Related Patterns

- `patterns/entity/event-sourced/` - For trip history
- `patterns/saga/distributed-transaction/` - For ride booking