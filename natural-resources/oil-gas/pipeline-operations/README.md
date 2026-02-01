# Pipeline Operations

Flow management, custody transfer, and scheduling.

## Scope

This model covers pipeline operations, including:

- Pipeline network and metering
- Flow scheduling and nominations
- Custody transfer and measurement
- Leak detection and response
- Regulatory compliance

## Key Concepts

| Concept | Description |
|---------|-------------|
| Pipeline | A transport conduit with segments |
| Meter | A custody transfer measurement point |
| Nomination | A scheduled transport quantity |
| CustodyTransfer | Change of product ownership |

## Related Patterns

- `patterns/entity/event-sourced/` - For flow history
- `patterns/workflow/process-manager/` - For scheduling
