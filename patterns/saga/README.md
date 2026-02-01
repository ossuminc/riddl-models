# Saga Patterns

Patterns for distributed transactions and multi-step processes with compensation.

## Available Patterns

| Pattern | Description |
|---------|-------------|
| `distributed-transaction/` | Multi-step process with compensation logic |

## When to Use

- Need to coordinate changes across multiple bounded contexts
- Require rollback/compensation when steps fail
- Implementing long-running business processes

## Key Concepts

- **Step**: Individual action in the saga
- **Do**: Forward action to perform
- **Undo**: Compensation action on failure