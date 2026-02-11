# PLM Integration

CAD integration, BOM management, and engineering change.

## NAICS Code

**541330** - Engineering Services

## Scope

This model covers PLM integration, including:

- CAD file management and versioning
- Engineering BOM creation and maintenance
- Change request and change order workflows
- Release to manufacturing
- Document control

## Key Concepts

| Concept | Description |
|---------|-------------|
| Part | A designed component with metadata |
| EBOM | Engineering Bill of Materials |
| ChangeOrder | An approved design modification |
| Release | Approval for manufacturing use |

## Related Patterns

- `patterns/entity/event-sourced/` - For change history
- `patterns/saga/distributed-transaction/` - For ECO workflows
