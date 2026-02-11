# Ride Sharing

On-demand ride matching, dispatch, and payment processing.

## NAICS Code

**485310** - Taxi and Ridesharing Services

## Scope

This model covers ride-sharing operations, including:

- Rider request and driver matching
- Real-time dispatch and navigation
- Fare calculation and surge pricing
- Driver and rider ratings
- Payment processing and settlements

## Key Concepts

| Concept | Description |
|---------|-------------|
| RideRequest | A passenger's request for transportation |
| Driver | An available operator with vehicle and location |
| Match | The pairing of rider and driver |
| Trip | An active ride from pickup to dropoff |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For ride lifecycle
- `patterns/projection/read-model/` - For driver availability matching
