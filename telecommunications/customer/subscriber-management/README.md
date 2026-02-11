# Subscriber Management

Account, plan, and device management for telecom subscribers.

## NAICS Code

**517311** - Wired Telecommunications Carriers

## Scope

This model covers subscriber management, including:

- Account creation and management
- Plan selection and changes
- Device provisioning and SIM management
- Usage monitoring and alerts
- Self-service portal operations

## Key Concepts

| Concept | Description |
|---------|-------------|
| Subscriber | A customer with telecom services |
| Account | Billing and service relationship |
| Plan | A service bundle with pricing |
| Device | Customer equipment (phone, SIM) |

## Related Patterns

- `patterns/entity/event-sourced/` - For subscriber history
- `patterns/saga/distributed-transaction/` - For plan changes
