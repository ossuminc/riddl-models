# Projector Pattern (Read Model)

Builds and maintains a read-optimized view of data by consuming events. Used
for CQRS (Command Query Responsibility Segregation) patterns.

## When to Use

- Need read-optimized views different from write model
- Building dashboards or reports
- Implementing CQRS pattern
- Need denormalized data for fast queries

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{ProjectorName}` | The projector name (e.g., `OrderSummaryView`) |
| `{ViewName}` | The view record name (e.g., `OrderSummary`) |
| `{EntityName}` | The source entity name (e.g., `Order`) |

## Key Elements

- **record**: The view structure optimized for queries
- **handler**: Reacts to events and updates the view

## Characteristics

- **Eventually Consistent**: Views may lag behind writes
- **Rebuildable**: Can replay events to rebuild view
- **Query-Optimized**: Structure matches query patterns

## Usage

1. Copy `template.riddl`
2. Replace placeholders with your names
3. Define view record fields for your queries
4. Add handlers for relevant events