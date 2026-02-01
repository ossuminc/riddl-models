# Workflow Patterns

Patterns for process orchestration and state machines.

## Available Patterns

| Pattern | Description |
|---------|-------------|
| `process-manager/` | Event-driven workflow coordination |

## When to Use

- Workflow is event-driven rather than command-driven
- Need to react to events from multiple sources
- Process flow depends on external conditions

## Key Concepts

- **Process State**: Tracks workflow progress
- **Event Reactions**: Handlers respond to domain events
- **Command Issuance**: Process manager issues commands to advance workflow