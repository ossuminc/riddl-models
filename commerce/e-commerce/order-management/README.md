# Order Management

Order lifecycle from placement through fulfillment.

## Overview

This model tracks orders from initial placement through payment, fulfillment,
shipping, and delivery, including cancellations and returns.

## Key Entities

- **Order** - The order aggregate with line items and status
- **OrderItem** - Individual products ordered
- **Shipment** - Fulfillment and tracking information

## Commands

- `PlaceOrder` - Create a new order
- `ConfirmPayment` - Record successful payment
- `ShipOrder` - Mark order as shipped
- `CancelOrder` - Cancel an order
- `RequestReturn` - Initiate return process

## Events

- `OrderPlaced` - New order was created
- `PaymentConfirmed` - Payment was successful
- `OrderShipped` - Order was dispatched
- `OrderDelivered` - Order was delivered
- `OrderCancelled` - Order was cancelled

## Integration Points

- Payment gateway for transactions
- Inventory for allocation
- Shipping carriers for delivery
- Customer service for support