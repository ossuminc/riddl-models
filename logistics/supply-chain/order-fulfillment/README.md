# Order Fulfillment

Supply chain order processing from allocation through delivery.

## NAICS Code

**493110** - General Warehousing and Storage

## Scope

This model covers order fulfillment operations, including:

- Fulfillment order creation from sales orders
- Inventory allocation and backorder handling
- Pick task assignment and execution
- Packing and packing slip generation
- Shipment coordination and carrier selection
- Delivery confirmation and order completion

## Key Concepts

| Concept | Description |
|---------|-------------|
| FulfillmentOrder | A warehouse order to pick, pack, and ship |
| OrderLine | A line item with SKU and quantities |
| PickTask | A task to retrieve items from a bin location |
| PackingSlip | Packing details for a shipped order |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For fulfillment workflow
- `patterns/workflow/process-manager/` - For pick-pack-ship process
