# E-Commerce

Online retail and digital commerce models for direct-to-consumer sales.

## Scope

This subsector covers businesses that sell products or services directly to
consumers through digital channels, including:

- Online storefronts and shopping experiences
- Digital product catalogs and merchandising
- Shopping cart and checkout workflows
- Order lifecycle management
- Customer accounts and preferences

## Models

| Model | Description |
|-------|-------------|
| `shopping-cart/` | Customer cart management with add/remove/checkout |
| `order-management/` | Order lifecycle from placement to fulfillment |
| `product-catalog/` | Product listings, categories, and search |

## Related Patterns

- `patterns/entity/event-sourced/` - For cart and order state tracking
- `patterns/saga/distributed-transaction/` - For checkout workflows
- `patterns/projection/read-model/` - For product search optimization