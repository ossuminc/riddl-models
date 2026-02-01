# Process Manager Pattern

Coordinates complex workflows by reacting to events and issuing commands.
Similar to a saga but driven by external events rather than explicit steps.

## When to Use

- Workflow is event-driven rather than command-driven
- Need to react to events from multiple sources
- Process flow depends on external conditions
- Orchestrating long-running business processes

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{ProcessName}` | The process name (e.g., `OrderFulfillment`) |

## Key Elements

- **Process State**: Tracks workflow progress
- **Event Reactions**: Handlers respond to domain events
- **Command Issuance**: Manager issues commands to advance workflow

## Saga vs Process Manager

| Saga | Process Manager |
|------|-----------------|
| Explicit steps | Event-driven reactions |
| Command-initiated | Event-initiated |
| Sequential by default | Parallel possible |

## Usage

1. Copy `template.riddl`
2. Replace `{ProcessName}` with your process name
3. Define process states
4. Add handlers for relevant events
5. Issue commands to progress workflow