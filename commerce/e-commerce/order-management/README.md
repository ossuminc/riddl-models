# Order Management

Order lifecycle from placement through fulfillment.

## NAICS Code

**454110** - Electronic Shopping and Mail-Order Houses

## Overview

This model tracks orders from initial placement through payment, fulfillment,
shipping, and delivery, including cancellations and returns.

## Key Entities

- **Order** - The order aggregate with line items and status tracking
- **OrderItem** - Individual products ordered with quantity and pricing
- **Shipment** - Fulfillment and tracking information for deliveries
- **Return** - Handles return requests, refunds, and restocking

## States

The Order entity progresses through these states:

- `Draft` - Order created but not yet submitted
- `Pending` - Order placed, awaiting payment confirmation
- `Confirmed` - Payment confirmed, ready for fulfillment
- `Shipped` - Order dispatched to carrier
- `Delivered` - Order successfully delivered
- `Cancelled` - Order cancelled (before shipment)
- `Returned` - Order returned after delivery

## Commands

- `PlaceOrder` - Create a new order from cart items
- `ConfirmPayment` - Record successful payment from gateway
- `AllocateInventory` - Reserve inventory for order items
- `ShipOrder` - Mark order as shipped with tracking info
- `DeliverOrder` - Mark order as delivered
- `CancelOrder` - Cancel an order (pre-shipment only)
- `RequestReturn` - Initiate return process
- `ProcessRefund` - Process refund for returned items

## Events

- `OrderPlaced` - New order was created
- `PaymentConfirmed` - Payment was successful
- `InventoryAllocated` - Inventory reserved for order
- `OrderShipped` - Order was dispatched with tracking
- `OrderDelivered` - Order was delivered to customer
- `OrderCancelled` - Order was cancelled
- `ReturnRequested` - Return was initiated
- `RefundProcessed` - Refund was completed

## Sagas

- **OrderFulfillmentSaga** - Orchestrates the complete order lifecycle from
  payment through delivery, with compensation for failures at each step

## Integration Points (External Contexts)

- **PaymentGateway** - Processes payments and refunds
- **InventoryService** - Manages stock allocation and availability
- **ShippingCarrier** - Handles shipment creation and tracking
- **CustomerService** - Manages customer communication and support tickets

## File Structure

```
order-management/
├── order-management.riddl      # Domain entry point
├── OrderContext.riddl          # Main bounded context
├── Order.riddl                 # Order entity
├── Shipment.riddl              # Shipment entity
├── Return.riddl                # Return entity
├── types.riddl                 # Shared types
├── OrderFulfillmentSaga.riddl  # Fulfillment orchestration
└── external-contexts.riddl     # External system integrations
```
