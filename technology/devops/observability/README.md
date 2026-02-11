# Observability

Monitoring, logging, tracing, and alerting for systems.

## NAICS Code

**541512** - Computer Systems Design Services

## Overview

This model handles observability operations including alert lifecycle
management from firing through acknowledgment, escalation, and
resolution, with integration to metrics, logs, and traces.

## Key Entities

- **Alert** - Alert instance from firing to resolution

## Commands

- `CreateAlert` - Fire a new alert
- `AcknowledgeAlert` - Claim an alert
- `ResolveAlert` - Mark alert as resolved
- `SilenceAlert` - Silence an alert
- `EscalateAlert` - Escalate alert severity
- `AddComment` - Add comment to alert
- `ExpireAlert` - Expire an alert automatically

## Events

- `AlertCreated` - Alert fired
- `AlertAcknowledged` - Responder engaged
- `AlertResolved` - Alert resolved
- `AlertSilenced` - Alert silenced
- `AlertEscalated` - Alert escalated
- `CommentAdded` - Comment added
- `AlertExpired` - Alert expired

## Integration Points

- Metrics collection (Prometheus, DataDog)
- Log aggregation (Elasticsearch, Loki)
- Distributed tracing (Jaeger, Tempo)
- Notification services (PagerDuty, Slack, OpsGenie)
- Dashboard services (Grafana)
