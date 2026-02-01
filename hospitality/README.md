# Hospitality & Travel

RIDDL models for lodging, food service, travel, and events.

## Subsectors

### lodging/
Hotel and accommodation operations.

**Models:**
- `property-management/` - Rooms, rates, availability
- `reservation-system/` - Booking, modifications, cancellations
- `guest-services/` - Check-in, requests, checkout

### food-service/
Restaurant and catering operations.

**Models:**
- `restaurant-operations/` - Orders, kitchen, service
- `catering-management/` - Events, menus, logistics

### travel/
Transportation booking and tour operations.

**Models:**
- `airline-reservations/` - Flights, seats, upgrades
- `car-rental/` - Fleet, reservations, returns
- `tour-operations/` - Packages, excursions, guides

### events/
Event venue and registration management.

**Models:**
- `venue-management/` - Spaces, bookings, setup
- `event-registration/` - Tickets, attendees, check-in

## Common Patterns

Hospitality models frequently use:
- Saga patterns for booking workflows (reserve → confirm → notify)
- Explicit states for reservation lifecycle
- Projectors for availability calendars
- Integration adapters for channel management (OTAs)

## Domain-Specific Concepts

- **ADR** - Average Daily Rate
- **RevPAR** - Revenue per Available Room
- **OTA** - Online Travel Agency