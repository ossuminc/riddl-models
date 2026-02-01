# Order Orchestration

Multi-vendor order splitting and coordination.

## Overview

This model handles marketplace orders that span multiple vendors, splitting
orders, coordinating fulfillment, and consolidating tracking.

## Key Entities

- **MarketplaceOrder** - Customer order potentially spanning vendors
- **VendorOrder** - Portion assigned to a specific vendor
- **Fulfillment** - Vendor fulfillment tracking

## Commands

- `SplitOrder` - Divide order among vendors
- `AssignToVendor` - Route items to vendor
- `ConfirmFulfillment` - Vendor ships their portion
- `ConsolidateTracking` - Merge tracking info
- `HandleException` - Manage fulfillment issues

## Events

- `OrderSplit` - Order was divided
- `VendorOrderCreated` - Vendor portion assigned
- `VendorShipped` - Vendor fulfilled their items
- `AllItemsShipped` - Complete order shipped
- `FulfillmentException` - Issue occurred

## Integration Points

- Vendor management for routing
- Shipping carriers for tracking
- Customer notifications
- Dispute resolution