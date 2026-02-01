# Marketplace

Multi-vendor marketplace platforms connecting buyers and sellers.

## Scope

This subsector covers platforms where multiple vendors sell through a common
storefront, including:

- Vendor onboarding and management
- Multi-seller product listings
- Order routing and fulfillment coordination
- Commission and payment distribution
- Seller performance and ratings

## Models

| Model | Description |
|-------|-------------|
| `vendor-management/` | Seller onboarding, profiles, and compliance |
| `order-orchestration/` | Multi-vendor order splitting and routing |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For multi-vendor order coordination
- `patterns/entity/aggregate-root/` - For vendor profile management