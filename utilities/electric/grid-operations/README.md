# Grid Operations

Electric generation, transmission, and distribution management.

## Scope

This model covers grid operations, including:

- Generation dispatch and scheduling
- Transmission network monitoring
- Distribution feeder management
- Load forecasting and balancing
- DER integration and management

## Key Concepts

| Concept | Description |
|---------|-------------|
| Generator | A power generation asset |
| Substation | A voltage transformation facility |
| Feeder | A distribution circuit |
| Load | Aggregated power consumption |

## Related Patterns

- `patterns/projection/read-model/` - For real-time grid status
- `patterns/entity/event-sourced/` - For operational history
