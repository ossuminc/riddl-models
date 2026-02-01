# Asset Management

Investment management for institutional and retail clients.

## Scope

This subsector covers the management of investment portfolios on behalf of
clients, including:

- Portfolio construction and rebalancing
- Trade execution and allocation
- Performance measurement and attribution
- Client reporting and statements
- Regulatory compliance (ADV, Form PF)

## Models

| Model | Description |
|-------|-------------|
| `investment-portfolio/` | Holdings, allocations, and rebalancing |
| `client-reporting/` | Statements, performance, and communications |

## Related Patterns

- `patterns/entity/event-sourced/` - For portfolio transaction history
- `patterns/projection/read-model/` - For performance calculations