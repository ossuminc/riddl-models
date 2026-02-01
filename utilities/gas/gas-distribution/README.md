# Gas Distribution

Natural gas metering, pressure management, and safety operations.

## Scope

This model covers gas distribution operations, including:

- Meter installation and reading
- Pressure monitoring and regulation
- Leak detection and response
- Service connections and disconnects
- Safety compliance and inspections

## Key Concepts

| Concept | Description |
|---------|-------------|
| Meter | A gas consumption measurement device |
| ServicePoint | A customer connection to the network |
| Pressure | Monitored pressure at network points |
| LeakReport | A detected or reported gas leak |

## Related Patterns

- `patterns/entity/event-sourced/` - For meter reading history
- `patterns/workflow/process-manager/` - For leak response
