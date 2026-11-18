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

- **`event-sourced entity`**: The intention keyword declares event sourcing
- **Commands**: Requests to change state
- **Events**: Facts about what happened
- **Handler**: Processes commands, emits events, transitions state

## Creation

An instance comes into being only through `create`, which runs the entity's
`on init` with the creator's arguments. So the creating command belongs to
the **context**, not the entity, because there is no instance yet to send it
to:

```riddl
on openAccount: command Accounts.OpenAccount is {
  let newAccount = create entity Accounts.Account(owner = openAccount.ownerName, ...)
  yield event Account.AccountOpened(accountId = newAccount, ...)
}
```

The entity's `on init` morphs into the state it starts in, chosen from its
arguments. There is no initial state. For an event-sourced entity, the
`on init` invocation is the instance's first journal entry and replay
re-runs it, so `on init` needs no creation event of its own to fold. The
creation event still exists: the context yields it to carry the new id back,
and `on init` sends it on for the repository.

## Usage

1. Copy `template.riddl`
2. Replace `{EntityName}` with your entity name
3. Add domain-specific fields to commands, events, and states
4. Implement validation logic in handlers

## Example

See `example.riddl` for a concrete Account entity implementation.