# Hospitals

Inpatient care, ancillary services, and hospital operations.

## Scope

This subsector covers acute care hospital operations, including:

- Admission, discharge, and transfer (ADT)
- Nursing workflow and documentation
- Operating room scheduling
- Laboratory and radiology orders
- Hospital supply chain and materials

## Models

| Model | Description |
|-------|-------------|
| `admission-discharge/` | Patient flow and bed management |
| `nursing-workflow/` | Shift handoffs, tasks, and documentation |
| `operating-room/` | Surgery scheduling and turnover |
| `lab-orders/` | Laboratory test ordering and results |
| `radiology-workflow/` | Imaging orders and interpretation |
| `supply-chain/` | Medical supplies and inventory |

## Related Patterns

- `patterns/workflow/process-manager/` - For clinical pathways
- `patterns/entity/event-sourced/` - For patient journey tracking