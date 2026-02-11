# Email Marketing

Email campaign creation, audience targeting, and delivery tracking.

## NAICS Code

**541810** - Advertising Agencies

## Scope

This model covers email marketing operations, including:

- Campaign creation with templates and send settings
- Audience targeting via mailing lists and segments
- A/B testing configuration
- Campaign scheduling and immediate sending
- Delivery metrics tracking (sent, delivered, bounced)
- Subscriber engagement recording (opens, clicks)
- Campaign pause, resume, and cancellation

## Key Concepts

| Concept | Description |
|---------|-------------|
| EmailCampaign | A targeted email send to subscribers |
| EmailTemplate | Reusable email content and layout |
| AudienceSegment | A filtered subset of subscribers |
| EngagementRates | Open rate, click rate, and unsubscribe rate |

## Related Patterns

- `patterns/workflow/process-manager/` - For campaign send workflow
- `patterns/entity/event-sourced/` - For campaign lifecycle history
