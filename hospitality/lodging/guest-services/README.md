# Guest Services

Concierge and amenity management.

## NAICS Code

**721110** - Hotels and Motels

## Overview

This model manages guest services including requests, amenities,
and service recovery.

## Key Entities

- **Request** - Guest service ask
- **Amenity** - Service offering
- **Incident** - Service issue

## Commands

- `SubmitRequest` - Guest asks
- `FulfillRequest` - Complete ask
- `ReserveAmenity` - Book service
- `ReportIncident` - Log issue
- `ResolveIncident` - Fix issue

## Events

- `RequestSubmitted` - Guest asked
- `RequestFulfilled` - Ask completed
- `AmenityReserved` - Service booked
- `IncidentReported` - Issue logged
- `IncidentResolved` - Issue fixed

## Integration Points

- Property management
- Reservations
- Billing/POS
- Staff management