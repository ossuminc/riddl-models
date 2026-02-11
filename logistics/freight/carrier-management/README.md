# Carrier Management

Freight carrier onboarding, credentialing, and performance management.

## NAICS Code

**488510** - Freight Transportation Arrangement

## Scope

This model covers carrier management operations, including:

- Carrier registration and credential verification
- Insurance policy management
- Service area and rate configuration
- Carrier activation, suspension, and reinstatement
- Performance metrics tracking and rankings
- Capacity management

## Key Concepts

| Concept | Description |
|---------|-------------|
| Carrier | A freight transportation provider |
| InsurancePolicy | Carrier insurance coverage details |
| ServiceArea | Geographic regions a carrier serves |
| RateInfo | Shipping rate by origin/destination zone |
| PerformanceMetrics | On-time delivery, claims, and scores |

## Related Patterns

- `patterns/entity/event-sourced/` - For carrier lifecycle history
- `patterns/projection/read-model/` - For carrier performance rankings
