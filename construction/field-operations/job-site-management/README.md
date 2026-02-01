# Job Site Management

Daily logs, inspections, and safety operations.

## Scope

This model covers job site operations, including:

- Daily activity logs and progress
- Safety inspections and incidents
- Quality inspections and punch lists
- Weather and delay tracking
- Crew and visitor management

## Key Concepts

| Concept | Description |
|---------|-------------|
| DailyLog | A record of site activities |
| Inspection | A safety or quality check |
| Incident | A safety event requiring documentation |
| PunchList | Items requiring completion or repair |

## Related Patterns

- `patterns/entity/event-sourced/` - For daily log history
- `patterns/workflow/process-manager/` - For inspection workflows
