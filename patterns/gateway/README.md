# Gateway Patterns

Patterns for API facades and external integrations.

## Available Patterns

| Pattern | Description |
|---------|-------------|
| `api-gateway/` | Unified API facade for multiple contexts |

## When to Use

- Need a single entry point for external clients
- Want to aggregate responses from multiple contexts
- Require protocol translation or rate limiting

## Key Concepts

- **Facade**: Simplified interface hiding internal complexity
- **Router**: Directs requests to appropriate contexts
- **Adapter**: Translates between external and internal protocols