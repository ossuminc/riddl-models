# Intermodal Transportation

Container management and multi-mode freight coordination.

## NAICS Code

**488510** - Freight Transportation Arrangement

## Scope

This model covers intermodal operations, including:

- Container tracking and status
- Drayage scheduling and dispatch
- Rail and truck coordination
- Equipment interchange and detention
- Terminal operations and appointments

## Key Concepts

| Concept | Description |
|---------|-------------|
| Container | A shipping container with location and status |
| Drayage | Short-haul trucking between terminals |
| Interchange | The transfer of equipment between carriers |
| BookingOrder | A multi-leg transport arrangement |

## Related Patterns

- `patterns/workflow/process-manager/` - For multi-leg coordination
- `patterns/projection/read-model/` - For container visibility
