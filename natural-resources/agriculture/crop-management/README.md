# Crop Management

Agricultural crop production and field management operations.

## NAICS Code

**111000** - Crop Production

## Scope

This model covers crop management operations, including:

- Field registration and preparation
- Crop planting and growth tracking
- Chemical and fertilizer application recording
- Field scouting and health monitoring
- Irrigation management
- Harvest operations and yield recording

## Key Concepts

| Concept | Description |
|---------|-------------|
| Field | A defined area for cultivation with soil and acreage |
| PlantingRecord | Crop planting details with seed rate and spacing |
| ApplicationRecord | Chemical or fertilizer application event |
| ScoutingReport | Field observation for pests, disease, and weeds |
| HarvestRecord | Crop harvest data with yield and quality |

## Related Patterns

- `patterns/entity/event-sourced/` - For field lifecycle history
- `patterns/projection/read-model/` - For yield analytics
