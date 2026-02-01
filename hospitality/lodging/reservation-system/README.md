# Reservation System

Booking and availability management.

## Overview

This model manages hotel reservations including availability, booking,
modifications, and cancellations.

## Key Entities

- **Reservation** - Booking record
- **Availability** - Room inventory
- **Rate** - Pricing tier

## Commands

- `SearchAvailability` - Find rooms
- `CreateReservation` - Book stay
- `ModifyReservation` - Change booking
- `CancelReservation` - Cancel stay
- `ConfirmReservation` - Guarantee booking

## Events

- `AvailabilitySearched` - Rooms found
- `ReservationCreated` - Stay booked
- `ReservationModified` - Booking changed
- `ReservationCancelled` - Stay cancelled
- `ReservationConfirmed` - Booking guaranteed

## Integration Points

- Channel managers
- Revenue management
- Property management
- Payment systems