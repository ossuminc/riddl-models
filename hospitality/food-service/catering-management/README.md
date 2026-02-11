# Catering Management

Event catering operations from booking through delivery.

## NAICS Code

**722320** - Caterers

## Scope

This model covers catering business operations, including:

- Event bookings and client requirements
- Menu planning and customization
- Staff and equipment scheduling
- Food preparation coordination
- Delivery and on-site service logistics

## Key Concepts

| Concept | Description |
|---------|-------------|
| CateringEvent | A booked catering engagement with date, venue, and guest count |
| Menu | Configured food and beverage selections for an event |
| ServiceStaff | Personnel assigned to event preparation and service |
| DeliverySchedule | Timeline for food prep, transport, and setup |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For booking confirmation workflows
- `patterns/workflow/process-manager/` - For event day coordination
