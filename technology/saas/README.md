# SaaS (Software as a Service)

Multi-tenant software delivery and subscription business models.

## Scope

This subsector covers the operational aspects of delivering software as a
service, including:

- Multi-tenant architecture and isolation
- Subscription lifecycle management
- Usage tracking and metering
- Customer success and retention
- Tenant provisioning and configuration

## Models

| Model | Description |
|-------|-------------|
| `subscription-management/` | Plan tiers, billing cycles, and renewals |
| `tenant-provisioning/` | New customer onboarding and setup |
| `usage-metering/` | Consumption tracking for usage-based billing |
| `customer-success/` | Health scores, engagement, and churn prevention |

## Related Patterns

- `patterns/entity/aggregate-root/` - For tenant account management
- `patterns/projection/read-model/` - For usage dashboards