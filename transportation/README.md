# Transportation

RIDDL models for freight, passenger, fleet, and maritime transportation.

## Subsectors

### freight/
Freight forwarding and cargo operations.

**Models:**
- `freight-forwarding/` - Booking, documentation, tracking
- `customs-brokerage/` - Classification, compliance, clearance
- `intermodal/` - Container management, drayage

### passenger/
Passenger transportation services.

**Models:**
- `transit-operations/` - Routes, schedules, real-time tracking
- `ride-sharing/` - Matching, dispatch, payments

### fleet/
Commercial fleet management.

**Models:**
- `fleet-management/` - Vehicles, drivers, compliance
- `route-optimization/` - Planning, dispatch, tracking

### maritime/
Shipping and port operations.

**Models:**
- `port-operations/` - Berth, cargo, terminal
- `vessel-management/` - Voyage, crew, maintenance

## Common Patterns

Transportation models frequently use:
- Real-time projectors for tracking dashboards
- Saga patterns for booking workflows
- Event sourcing for shipment history
- Integration adapters for telematics and GPS

## Domain-Specific Concepts

- **BOL** - Bill of Lading
- **ETA/ETD** - Estimated Time of Arrival/Departure
- **Drayage** - Short-haul container transport
- **TEU** - Twenty-foot Equivalent Unit (container)