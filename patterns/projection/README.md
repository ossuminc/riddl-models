# Projection Patterns

Patterns for CQRS read models and views.

## Available Patterns

| Pattern | Description |
|---------|-------------|
| `read-model/` | Read-optimized view built from event streams |

## When to Use

- Need read-optimized views different from write model
- Building dashboards or reports
- Implementing CQRS (Command Query Responsibility Segregation)

## Key Concepts

- **Record**: The view structure optimized for queries
- **Handler**: Reacts to events and updates the view
- **Eventual Consistency**: Views may lag behind writes