# Ad Serving

Digital advertising delivery, targeting, and impression tracking.

## NAICS Code

**541890** - Other Services Related to Advertising

## Scope

This model covers ad serving operations, including:

- Ad creation with creative assets and targeting
- Bid configuration (CPM, CPC, CPA, CPCV, Fixed)
- Flight scheduling with budget and impression goals
- Ad activation, pausing, and completion
- Impression and click recording
- Campaign-level performance analytics (CTR, eCPM)

## Key Concepts

| Concept | Description |
|---------|-------------|
| Ad | A digital advertisement with creative and targeting |
| AdCreative | Visual or media asset served to users |
| TargetingCriteria | Audience parameters (geo, age, interests) |
| DeliveryStats | Impressions, clicks, spend, CTR, and eCPM |

## Related Patterns

- `patterns/entity/event-sourced/` - For ad delivery history
- `patterns/projection/read-model/` - For campaign performance dashboards
