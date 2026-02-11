# Hotel Reservations

Room booking, check-in/check-out, and guest management.

## NAICS Code

**721110** - Hotels and Motels

## Overview

This model manages hotel reservations including room booking,
guest check-in and check-out, folio charges, special requests,
cancellations, and no-show handling.

## Key Entities

- **Reservation** - Guest booking with room, dates, and rate plan
- **GuestInfo** - Guest profile with loyalty and preferences
- **RoomInfo** - Room details with type, floor, and amenities

## Commands

- `CreateReservation` - Book a room
- `ConfirmReservation` - Confirm with payment
- `ModifyReservation` - Change dates or room type
- `AddSpecialRequest` - Add guest request
- `CheckIn` - Check guest into assigned room
- `PostCharge` - Post charge to guest folio
- `CheckOut` - Check guest out with final payment
- `CancelReservation` - Cancel booking
- `MarkNoShow` - Record no-show with charge

## Events

- `ReservationCreated` - Booking made
- `ReservationConfirmed` - Payment confirmed
- `ReservationModified` - Booking changed
- `GuestCheckedIn` - Guest arrived
- `ChargePosted` - Folio charge added
- `GuestCheckedOut` - Guest departed
- `ReservationCancelled` - Booking cancelled
- `NoShowRecorded` - Guest did not arrive

## Integration Points

- Channel managers (OTA distribution)
- Payment gateway
- Housekeeping service
- Loyalty program
- Guest communications
