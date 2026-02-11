# Returns Processing

RMA, inspection, and disposition for returned goods.

## NAICS Code

**493110** - General Warehousing and Storage

## Scope

This model covers returns processing, including:

- Return authorization (RMA) creation
- Receipt and inspection
- Disposition determination
- Restocking or disposal
- Refund and credit processing

## Key Concepts

| Concept | Description |
|---------|-------------|
| RMA | Authorization for a product return |
| Inspection | Examination of returned goods |
| Disposition | Decision on item fate (restock, scrap) |
| Credit | Refund or account credit issued |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For refund workflow
- `patterns/workflow/process-manager/` - For disposition
