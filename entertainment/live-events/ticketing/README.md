# Ticketing

Event ticket sales, seating, and access control.

## NAICS Code

**711310** - Promoters of Performing Arts and Similar Events

## Scope

This model covers ticketing operations, including:

- Event setup and pricing tiers
- Seat inventory and holds
- Ticket purchase and payment
- Digital ticket delivery
- Venue access control and scanning

## Key Concepts

| Concept | Description |
|---------|-------------|
| Event | A ticketed show or performance |
| Ticket | An admission right to an event |
| Seat | A specific location with availability status |
| Order | A ticket purchase transaction |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For purchase workflows
- `patterns/projection/read-model/` - For seat availability maps
