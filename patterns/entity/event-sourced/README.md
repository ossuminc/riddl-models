# Event-Sourced Entity Pattern

An entity that persists state changes as a sequence of events. All state
changes are captured as events, enabling full audit trail and temporal queries.

## When to Use

- Need complete audit history of all changes
- Want to support temporal queries ("what was the state on date X?")
- Building event-driven systems with eventual consistency
- Need event replay for debugging or rebuilding state

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{EntityName}` | The name of your entity (e.g., `Order`, `Account`) |

## Key Elements

- **`option event-sourced`**: Declares event sourcing (required!)
- **Commands**: Requests to change state
- **Events**: Facts about what happened
- **Handler**: Processes commands, emits events, transitions state

## Usage

1. Copy `template.riddl`
2. Replace `{EntityName}` with your entity name
3. Add domain-specific fields to commands, events, and states
4. Implement validation logic in handlers

## Example

See `example.riddl` for a concrete Account entity implementation.