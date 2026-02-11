# Log Tracking

Log scaling, transport, and mill delivery.

## NAICS Code

**113310** - Logging

## Scope

This model covers log tracking operations, including:

- Log scaling and grading
- Load ticketing and transport
- Mill receiving and verification
- Chain of custody documentation
- Payment settlement

## Key Concepts

| Concept | Description |
|---------|-------------|
| Log | A harvested timber piece with scale |
| LoadTicket | A transport document with contents |
| Scale | Volume measurement and grading |
| Delivery | Receipt at destination mill |

## Related Patterns

- `patterns/entity/event-sourced/` - For chain of custody
- `patterns/saga/distributed-transaction/` - For settlement
