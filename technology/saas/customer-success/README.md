# Customer Success

Customer health and retention management.

## NAICS Code

**511210** - Software Publishers

## Overview

This model tracks customer health, engagement, and success metrics to
prevent churn and drive expansion.

## Key Entities

- **CustomerHealth** - Overall health score
- **Engagement** - Product usage patterns
- **SuccessPlan** - Customer goals and milestones

## Commands

- `CalculateHealth` - Update health score
- `CreateSuccessPlan` - Define customer goals
- `LogEngagement` - Record interaction
- `TriggerIntervention` - Initiate outreach
- `RecordMilestone` - Note achievement

## Events

- `HealthUpdated` - Score recalculated
- `HealthDeclined` - Risk detected
- `MilestoneAchieved` - Goal reached
- `InterventionTriggered` - Outreach initiated
- `ChurnRiskIdentified` - At-risk customer

## Integration Points

- Product analytics
- CRM systems
- Support ticketing
- Communication tools