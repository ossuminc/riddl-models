# Event Registration

Attendee registration, ticketing, and check-in for events and conferences.

## NAICS Code

**711310** - Promoters of Performing Arts, Sports, and Similar Events

## Scope

This model covers event registration operations, including:

- Ticket types and pricing tiers
- Attendee registration and payment processing
- Confirmation and badge generation
- Session and workshop selection
- On-site check-in and attendance tracking

## Key Concepts

| Concept | Description |
|---------|-------------|
| Registration | An attendee's enrollment for an event |
| Ticket | A purchased admission with specific access rights |
| Attendee | A person registered for the event |
| CheckIn | The on-site verification and badge issuance |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For registration and payment flow
- `patterns/entity/event-sourced/` - For attendee journey tracking
