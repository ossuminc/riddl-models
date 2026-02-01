# CNC Operations

CNC program management, tooling, and cycle tracking.

## Scope

This model covers CNC operations, including:

- NC program management and versioning
- Tool library and life tracking
- Setup sheets and work holding
- Cycle time monitoring
- Machine utilization tracking

## Key Concepts

| Concept | Description |
|---------|-------------|
| Program | NC code for machining operations |
| Tool | A cutting tool with life and wear data |
| Setup | Machine configuration for a job |
| Cycle | A completed machining operation |

## Related Patterns

- `patterns/entity/event-sourced/` - For program revisions
- `patterns/projection/read-model/` - For machine dashboards
