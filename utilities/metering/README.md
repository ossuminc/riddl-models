# Metering

Smart metering and utility billing.

## Scope

This subsector covers utility metering operations, including:

- Smart meter deployment
- Meter data management
- Usage billing and settlement
- Time-of-use pricing
- Demand response

## Models

| Model | Description |
|-------|-------------|
| `smart-metering/` | Meter reading, data collection, and validation |
| `billing-settlement/` | Usage calculation and invoice generation |

## Related Patterns

- `patterns/entity/event-sourced/` - For meter readings
- `patterns/projection/read-model/` - For usage analytics