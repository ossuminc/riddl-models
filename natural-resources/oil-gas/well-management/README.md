# Well Management

Drilling, completion, and production operations.

## NAICS Code

**211120** - Crude Petroleum Extraction

## Scope

This model covers well lifecycle management, including:

- Well planning and permitting
- Drilling operations and logs
- Completion and workover
- Production monitoring
- Abandonment and reclamation

## Key Concepts

| Concept | Description |
|---------|-------------|
| Well | A drilled bore for extraction |
| DrillingProgram | Planned operations and targets |
| Completion | Configuration for production |
| Production | Extracted volumes over time |

## Related Patterns

- `patterns/entity/event-sourced/` - For well lifecycle
- `patterns/projection/read-model/` - For production dashboards
