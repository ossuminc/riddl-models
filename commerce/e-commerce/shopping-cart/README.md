# Shopping Cart

Customer shopping cart management for e-commerce.

## NAICS Code

**454110** - Electronic Shopping and Mail-Order Houses

## Overview

This model manages the customer's shopping cart throughout their browsing
session, handling item additions, removals, quantity updates, and checkout
initiation.

## Key Entities

- **Cart** - The shopping cart aggregate containing items
- **CartItem** - Individual product line items with quantity and price

## Commands

- `AddItem` - Add a product to the cart
- `RemoveItem` - Remove a product from the cart
- `UpdateQuantity` - Change the quantity of an item
- `ApplyCoupon` - Apply a discount code
- `Checkout` - Initiate the checkout process

## Events

- `ItemAdded` - Product was added to cart
- `ItemRemoved` - Product was removed from cart
- `QuantityUpdated` - Item quantity was changed
- `CouponApplied` - Discount code was applied
- `CartCheckedOut` - Checkout was initiated

## Integration Points

- Product catalog for pricing and availability
- Inventory for stock validation
- Order management for checkout handoff
- Promotions engine for discount calculation