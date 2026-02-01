# Vessel Management

Ship operations, voyage planning, and crew management.

## Scope

This model covers vessel operations, including:

- Voyage planning and scheduling
- Crew certification and assignment
- Maintenance and dry-dock planning
- Fuel and provisions management
- Regulatory compliance and inspections

## Key Concepts

| Concept | Description |
|---------|-------------|
| Vessel | A ship with specifications and operational status |
| Voyage | A planned journey with ports of call |
| Crew | Personnel assigned to a vessel with certifications |
| MaintenanceSchedule | Planned service and inspection activities |

## Related Patterns

- `patterns/entity/event-sourced/` - For voyage and maintenance history
- `patterns/entity/aggregate-root/` - For vessel with crew assignments
