# Matter Management

Legal case tracking, tasks, and deadlines.

## Scope

This model covers legal matter management, including:

- Matter intake and conflict checking
- Task and deadline management
- Document management
- Time and expense tracking
- Billing and invoicing

## Key Concepts

| Concept | Description |
|---------|-------------|
| Matter | A legal case or project |
| Task | Work to be completed on a matter |
| Deadline | A critical date for filings or actions |
| TimeEntry | Billable time recorded |

## Related Patterns

- `patterns/entity/event-sourced/` - For matter history
- `patterns/entity/aggregate-root/` - For matter with tasks
