# Retail & Commerce

RIDDL models for e-commerce, brick-and-mortar retail, marketplaces, and
wholesale distribution.

## Subsectors

### e-commerce/
Online commerce operations.

**Models:**
- `shopping-cart/` - Cart, checkout, payment
- `product-catalog/` - Products, categories, pricing
- `order-management/` - Fulfillment, returns, exchanges

### retail/
Physical retail store operations.

**Models:**
- `point-of-sale/` - Transactions, tenders, receipts
- `inventory-management/` - Stock, replenishment, transfers
- `store-operations/` - Scheduling, cash management

### marketplace/
Multi-vendor marketplace operations.

**Models:**
- `vendor-management/` - Onboarding, catalog, settlement
- `order-orchestration/` - Multi-vendor fulfillment

### wholesale/
B2B distribution and trade credit.

**Models:**
- `distribution/` - B2B ordering, pricing tiers
- `trade-credit/` - Net terms, credit limits

## Common Patterns

Commerce models frequently use:
- Shopping cart as aggregate root
- Saga patterns for checkout (inventory reserve → payment → fulfillment)
- Projectors for product search and inventory views
- Event sourcing for order history

## Starter vs Enterprise

Commerce models often have complexity tiers:
- **starter** - Single store, basic inventory
- **standard** - Multi-location, promotions
- **enterprise** - Omnichannel, loyalty programs