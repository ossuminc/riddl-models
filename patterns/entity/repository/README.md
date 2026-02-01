# Repository Pattern

Provides persistence and query capabilities for entities. Abstracts the storage
mechanism from the domain logic.

## When to Use

- Need to persist and retrieve entities
- Want to separate storage concerns from domain logic
- Require complex query capabilities

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{RepositoryName}` | The repository name (e.g., `OrderRepository`) |
| `{EntityName}` | The entity being persisted (e.g., `Order`) |

## Key Elements

- **Store command**: Persist an entity
- **Find commands**: Query for entities
- **Delete command**: Remove an entity
- **Query type**: Criteria for searching

## Usage

1. Copy `template.riddl`
2. Replace `{RepositoryName}` and `{EntityName}`
3. Define query criteria fields
4. Implement storage operations in handlers