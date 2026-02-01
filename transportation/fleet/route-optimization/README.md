# Route Optimization

Delivery planning, dispatch, and real-time tracking.

## Scope

This model covers route planning operations, including:

- Daily route generation and optimization
- Stop sequencing and time windows
- Driver dispatch and mobile updates
- Real-time tracking and ETA updates
- Proof of delivery capture

## Key Concepts

| Concept | Description |
|---------|-------------|
| Route | An ordered sequence of stops for a vehicle |
| Stop | A delivery or pickup location with time window |
| Dispatch | The assignment of routes to drivers |
| Tracking | Real-time vehicle location and status |

## Related Patterns

- `patterns/projection/read-model/` - For real-time tracking dashboards
- `patterns/entity/event-sourced/` - For delivery history
