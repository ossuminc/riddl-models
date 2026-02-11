# Port Operations

Terminal and cargo handling at maritime ports.

## NAICS Code

**488310** - Port and Harbor Operations

## Scope

This model covers port terminal operations, including:

- Berth scheduling and vessel arrival
- Container yard management
- Cargo loading and unloading
- Gate operations and truck appointments
- Equipment allocation and tracking

## Key Concepts

| Concept | Description |
|---------|-------------|
| Berth | A dock position for vessel mooring |
| Terminal | A port facility handling specific cargo types |
| Container | A TEU/FEU unit with tracking and status |
| VesselCall | A scheduled port visit with arrival/departure times |

## Related Patterns

- `patterns/workflow/process-manager/` - For vessel turnaround coordination
- `patterns/projection/read-model/` - For yard inventory views
