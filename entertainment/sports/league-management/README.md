# League Management

Sports league administration, scheduling, and standings.

## Scope

This model covers league operations, including:

- Team and franchise management
- Season scheduling and fixtures
- Results recording and standings
- Playoff and tournament brackets
- Rule enforcement and disciplinary actions

## Key Concepts

| Concept | Description |
|---------|-------------|
| League | A sports organization with teams |
| Team | A franchise participating in the league |
| Season | A competitive period with schedule |
| Match | A scheduled game between teams |

## Related Patterns

- `patterns/entity/event-sourced/` - For match results history
- `patterns/projection/read-model/` - For standings calculations
