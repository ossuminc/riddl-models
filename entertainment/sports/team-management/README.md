# Team Management

Professional sports team roster and player lifecycle management.

## NAICS Code

**711211** - Sports Teams and Clubs

## Scope

This model covers team management operations, including:

- Player signing with contract terms and salary cap validation
- Roster assignment with position and jersey number
- Contract extensions and renegotiations
- Player trades between teams with league approval
- Injured reserve placement and return management
- Player release and free agency

## Key Concepts

| Concept | Description |
|---------|-------------|
| Player | An athlete with contract, roster status, and career data |
| Team | A franchise with roster limits and salary cap tracking |
| ContractInfo | Financial terms including salary, guarantees, and bonuses |
| RosterSlot | A player's position assignment on a team roster |
| TradeInfo | Details of a multi-party trade transaction |

## Related Patterns

- `patterns/entity/event-sourced/` - For player career history
- `patterns/saga/distributed-transaction/` - For trade workflows
