# Ticket Sales

Live event ticket management from creation through sale, transfer,
and refund.

## NAICS Code

**711310** - Promoters of Performing Arts and Similar Events

## Scope

This model covers ticket sales operations, including:

- Event creation with venue and pricing tier setup
- Ticket inventory release and availability management
- Seat reservation and purchase processing
- Ticket transfers between buyers
- Refund processing based on event policies
- Venue entry scanning and admission

## Key Concepts

| Concept | Description |
|---------|-------------|
| Ticket | An admission right with seat assignment and pricing |
| Event | A scheduled live performance with venue and pricing tiers |
| PricingTier | A price level with sections, fees, and inventory counts |
| TransferRecord | Audit trail of ticket ownership changes |
| SeatInfo | A specific venue seat with type and accessibility |

## Related Patterns

- `patterns/entity/event-sourced/` - For ticket lifecycle history
- `patterns/saga/distributed-transaction/` - For purchase workflows
- `patterns/projection/read-model/` - For sales metrics dashboards
