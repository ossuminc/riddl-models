# Saga Pattern (Distributed Transaction)

Coordinates a multi-step process across multiple entities or contexts with
compensation logic to handle failures.

## When to Use

- Need to coordinate changes across multiple bounded contexts
- Require rollback/compensation when steps fail
- Implementing long-running business processes
- Cannot use traditional ACID transactions

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{SagaName}` | The saga name (e.g., `PlaceOrder`, `TransferFunds`) |

## Key Elements

- **requires**: Input to start the saga
- **returns**: Output when saga completes
- **step**: Individual action with do/undo
- **do**: Forward action to perform
- **undo**: Compensation action on failure

## Compensation Strategy

When a step fails:
1. Stop executing forward steps
2. Execute undo for all completed steps (in reverse order)
3. Return failure result

## Usage

1. Copy `template.riddl`
2. Replace `{SagaName}` with your saga name
3. Define input/output for the saga
4. Add steps with do/undo actions
5. Ensure all undo actions are idempotent

## Example

See `example.riddl` for a fund transfer saga implementation.