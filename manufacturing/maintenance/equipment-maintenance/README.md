# Equipment Maintenance

Preventive, corrective, and condition-based maintenance.

## NAICS Code

**811310** - Commercial and Industrial Machinery Repair

## Scope

This model covers equipment maintenance, including:

- Preventive maintenance scheduling
- Work order generation and execution
- Spare parts management
- Condition monitoring integration
- Maintenance history and analytics

## Key Concepts

| Concept | Description |
|---------|-------------|
| Equipment | A maintainable asset |
| WorkOrder | A maintenance job with tasks |
| PMSchedule | Recurring preventive maintenance plan |
| Condition | Monitored equipment health metrics |

## Related Patterns

- `patterns/entity/event-sourced/` - For maintenance history
- `patterns/workflow/process-manager/` - For work order execution
