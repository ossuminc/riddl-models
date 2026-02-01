# Entity Patterns

Patterns for modeling aggregates and entities in RIDDL.

## Available Patterns

| Pattern | Description |
|---------|-------------|
| `event-sourced/` | Entity that persists changes as events |
| `aggregate-root/` | Entity managing a cluster of child entities |
| `repository/` | Persistence abstraction for entities |

## When to Use

- **Event-Sourced**: Need audit trail, temporal queries, or event replay
- **Aggregate Root**: Have parent-child relationships with transactional consistency
- **Repository**: Need to abstract storage from domain logic