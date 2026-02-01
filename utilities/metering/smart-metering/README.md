# Smart Metering

Advanced Metering Infrastructure (AMI) and usage analytics.

## Scope

This model covers smart metering operations, including:

- Meter deployment and configuration
- Automated meter reading
- Interval data collection
- Demand response signals
- Usage analytics and alerts

## Key Concepts

| Concept | Description |
|---------|-------------|
| SmartMeter | An AMI-enabled measurement device |
| Reading | Collected consumption or demand data |
| IntervalData | Time-series usage measurements |
| Alert | A notification for unusual patterns |

## Related Patterns

- `patterns/entity/event-sourced/` - For reading history
- `patterns/projection/read-model/` - For usage dashboards
