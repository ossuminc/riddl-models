# Fulfillment

Order fulfillment and returns processing.

## Scope

This subsector covers order fulfillment operations, including:

- Order allocation and sourcing
- Wave planning and execution
- Shipping and carrier selection
- Returns authorization and processing
- Fulfillment analytics

## Models

| Model | Description |
|-------|-------------|
| `order-fulfillment/` | Order release, allocation, and shipping |
| `returns-processing/` | RMA, receiving, and disposition |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For order workflows
- `patterns/workflow/process-manager/` - For wave processing