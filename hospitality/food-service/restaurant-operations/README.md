# Restaurant Operations

Table and order management.

## NAICS Code

**722511** - Full-Service Restaurants

## Overview

This model manages restaurant operations including table management,
order taking, and kitchen coordination.

## Key Entities

- **Table** - Seating location
- **Order** - Guest order
- **Ticket** - Kitchen ticket

## Commands

- `SeatGuests` - Assign table
- `TakeOrder` - Record items
- `SendToKitchen` - Fire ticket
- `DeliverFood` - Serve items
- `CloseCheck` - Complete payment

## Events

- `GuestsSeated` - Table assigned
- `OrderTaken` - Items recorded
- `TicketSent` - Kitchen notified
- `FoodDelivered` - Items served
- `CheckClosed` - Payment complete

## Integration Points

- POS systems
- Kitchen display
- Inventory
- Reservations