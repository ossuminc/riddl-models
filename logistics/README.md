# Supply Chain & Logistics

RIDDL models for warehousing, fulfillment, and supply chain operations.

## Subsectors

### warehousing/
Warehouse management operations.

**Models:**
- `warehouse-management/` - Receiving, putaway, picking, shipping
- `inventory-control/` - Counts, adjustments, transfers

### fulfillment/
Order fulfillment and returns.

**Models:**
- `order-fulfillment/` - Pick, pack, ship workflow
- `returns-processing/` - RMA, inspection, disposition

### supply-chain/
Supply chain planning and supplier management.

**Models:**
- `demand-planning/` - Forecasting, planning, allocation
- `supplier-management/` - Onboarding, performance, risk

## Common Patterns

Logistics models frequently use:
- Multi-state entities for inventory items and orders
- Saga patterns for fulfillment workflows
- Projectors for inventory visibility
- Integration adapters for carriers and WMS

## Domain-Specific Concepts

- **WMS** - Warehouse Management System
- **SKU** - Stock Keeping Unit
- **RMA** - Return Merchandise Authorization
- **FIFO/LIFO** - First/Last In First Out