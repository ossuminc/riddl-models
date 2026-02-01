# Aggregate Root Pattern

An entity that owns and coordinates a cluster of related entities. External
access to child entities goes through the aggregate root, maintaining
consistency.

## When to Use

- Have a natural parent-child relationship between entities
- Need transactional consistency across related objects
- Want to enforce invariants across multiple related entities
- Children should not be modified independently

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{AggregateName}` | The parent/root entity name (e.g., `Cart`, `Order`) |
| `{ChildName}` | The child entity name (e.g., `Item`, `Line`) |

## Key Concepts

- **Aggregate Boundary**: All changes go through the root
- **Child Collection**: Root maintains the collection of children
- **Invariants**: Root enforces rules across all children (e.g., max items)

## Usage

1. Copy `template.riddl`
2. Replace `{AggregateName}` with your root entity name
3. Replace `{ChildName}` with your child entity name
4. Add domain-specific fields and invariants

## Example

See `example.riddl` for a Shopping Cart with Line Items implementation.