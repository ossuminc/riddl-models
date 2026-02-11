# Livestock Management

Herd tracking, health management, and movement recording.

## NAICS Code

**112000** - Animal Production and Aquaculture

## Scope

This model covers livestock operations, including:

- Animal identification and registration
- Herd composition and breeding
- Health records and treatments
- Feed and nutrition management
- Movement and traceability

## Key Concepts

| Concept | Description |
|---------|-------------|
| Animal | An individual or group with identification |
| Herd | A managed group of animals |
| HealthEvent | Vaccinations, treatments, or illness |
| Movement | Transfer between locations |

## Related Patterns

- `patterns/entity/event-sourced/` - For animal history
- `patterns/entity/aggregate-root/` - For herd with animals
