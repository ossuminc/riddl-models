# Trading

Securities trading, order execution, and settlement.

## Scope

This subsector covers the buying and selling of financial instruments,
including:

- Order entry and routing
- Execution management
- Trade matching and confirmation
- Settlement and clearing
- Position and P&L tracking

## Models

| Model | Description |
|-------|-------------|
| `order-management/` | Order lifecycle from entry to execution |
| `trade-settlement/` | Post-trade clearing and settlement |

## Related Patterns

- `patterns/entity/event-sourced/` - For order state tracking
- `patterns/workflow/process-manager/` - For settlement workflows