# Fleet Management

Vehicle and driver administration for commercial fleets.

## NAICS Code

**484000** - Truck Transportation

## Scope

This model covers fleet administration, including:

- Vehicle inventory and specifications
- Driver qualification and assignment
- Maintenance scheduling and tracking
- Regulatory compliance (HOS, IFTA)
- Fuel management and cost tracking

## Key Concepts

| Concept | Description |
|---------|-------------|
| Vehicle | A fleet asset with specifications and status |
| Driver | A qualified operator with certifications |
| MaintenanceRecord | Service history and scheduled work |
| Compliance | Regulatory requirements and documentation |

## Related Patterns

- `patterns/entity/event-sourced/` - For vehicle lifecycle tracking
- `patterns/entity/aggregate-root/` - For vehicle with maintenance history
