# Car Rental

Vehicle fleet management and rental operations.

## NAICS Code

**532111** - Passenger Car Rental

## Scope

This model covers car rental operations, including:

- Vehicle fleet inventory and status
- Reservation and availability management
- Pickup and return processing
- Pricing, insurance, and add-ons
- Vehicle maintenance scheduling

## Key Concepts

| Concept | Description |
|---------|-------------|
| Vehicle | A rentable car with class, features, and status |
| Reservation | A booking for a vehicle class and time period |
| RentalAgreement | The contract for an active rental |
| Location | A pickup/return facility with fleet allocation |

## Related Patterns

- `patterns/entity/event-sourced/` - For vehicle lifecycle tracking
- `patterns/saga/distributed-transaction/` - For reservation confirmation
