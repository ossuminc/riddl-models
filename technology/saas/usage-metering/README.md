# Usage Metering

Consumption tracking for usage-based billing.

## Overview

This model tracks product usage for consumption-based pricing including
API calls, storage, compute, and custom metrics.

## Key Entities

- **UsageRecord** - Individual usage event
- **MeterDefinition** - What is being measured
- **UsageSummary** - Aggregated consumption

## Commands

- `RecordUsage` - Capture usage event
- `AggregateUsage` - Summarize period
- `ApplyRateCard` - Calculate charges
- `ResetMeter` - Clear period usage
- `AdjustUsage` - Correct usage data

## Events

- `UsageRecorded` - Event captured
- `UsageAggregated` - Period summarized
- `ChargesCalculated` - Billing amount determined
- `ThresholdReached` - Usage limit approached
- `OverageTriggered` - Exceeded included usage

## Integration Points

- Application instrumentation
- Billing systems
- Customer dashboards
- Alerting systems