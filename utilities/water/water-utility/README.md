# Water Utility

Water treatment, distribution, and billing operations.

## NAICS Code

**221310** - Water Supply and Irrigation Systems

## Scope

This model covers water utility operations, including:

- Water treatment and quality monitoring
- Distribution network management
- Meter reading and consumption
- Service orders and connections
- Billing and collections

## Key Concepts

| Concept | Description |
|---------|-------------|
| TreatmentPlant | A water processing facility |
| DistributionMain | A pipe in the water network |
| Meter | A water consumption measurement device |
| ServiceOrder | A work request for a service point |

## Related Patterns

- `patterns/entity/event-sourced/` - For consumption history
- `patterns/saga/distributed-transaction/` - For service orders
