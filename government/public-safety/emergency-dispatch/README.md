# Emergency Dispatch

Computer-Aided Dispatch (CAD) for emergency services.

## NAICS Code

**922160** - Fire Protection

## Scope

This model covers emergency dispatch operations, including:

- Call intake and triage
- Unit dispatch and tracking
- Incident management
- Resource allocation
- Inter-agency coordination

## Key Concepts

| Concept | Description |
|---------|-------------|
| Incident | An emergency event requiring response |
| Unit | A responding resource (vehicle, personnel) |
| Dispatch | The assignment of units to incidents |
| CADEvent | A timestamped action in incident handling |

## Related Patterns

- `patterns/entity/event-sourced/` - For complete incident timeline
- `patterns/projection/read-model/` - For real-time unit status
