# Work Order Management

Production scheduling, execution, and completion tracking.

## NAICS Code

**332000** - Fabricated Metal Product Manufacturing

## Scope

This model covers work order operations, including:

- Work order creation and scheduling
- Material allocation and picking
- Production execution tracking
- Labor and machine time recording
- Completion and variance reporting

## Key Concepts

| Concept | Description |
|---------|-------------|
| WorkOrder | A production job for a quantity of items |
| Operation | A step in the manufacturing routing |
| MaterialIssue | Components consumed for production |
| Completion | Finished goods received into inventory |

## Related Patterns

- `patterns/entity/event-sourced/` - For production history
- `patterns/saga/distributed-transaction/` - For material reservation
