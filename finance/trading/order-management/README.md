# Order Management

Securities order lifecycle.

## Overview

This model manages trading orders from entry through execution including
routing, fills, and order state management.

## Key Entities

- **Order** - Buy or sell instruction
- **Execution** - Fill information
- **Route** - Venue selection

## Commands

- `PlaceOrder` - Submit order
- `CancelOrder` - Cancel pending order
- `ModifyOrder` - Change order parameters
- `RouteOrder` - Select venue
- `ReportFill` - Record execution

## Events

- `OrderPlaced` - Order submitted
- `OrderRouted` - Sent to venue
- `OrderFilled` - Execution received
- `OrderCancelled` - Order cancelled
- `OrderRejected` - Order refused

## Integration Points

- Market data feeds
- Execution venues
- Risk management
- Position keeping