# Transit Operations

Public transportation routes, schedules, and real-time tracking.

## Scope

This model covers public transit operations, including:

- Route and schedule management
- Vehicle and operator assignment
- Real-time arrival predictions
- Fare collection and validation
- Service alerts and disruptions

## Key Concepts

| Concept | Description |
|---------|-------------|
| Route | A defined path with stops and schedule |
| Trip | A single vehicle journey along a route |
| Vehicle | A bus, train, or other transit asset |
| Arrival | Predicted or actual arrival at a stop |

## Related Patterns

- `patterns/projection/read-model/` - For real-time arrival boards
- `patterns/entity/event-sourced/` - For service history
