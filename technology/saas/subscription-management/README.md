# Subscription Management

SaaS subscription lifecycle and billing cycles.

## Overview

This model manages subscription plans, billing cycles, upgrades, downgrades,
and renewals for SaaS products.

## Key Entities

- **Subscription** - Customer subscription instance
- **Plan** - Available subscription tiers
- **BillingCycle** - Recurring billing period

## Commands

- `Subscribe` - Create new subscription
- `ChangePlan` - Upgrade or downgrade
- `CancelSubscription` - End subscription
- `RenewSubscription` - Process renewal
- `PauseSubscription` - Temporarily suspend

## Events

- `SubscriptionCreated` - New subscription started
- `PlanChanged` - Tier was changed
- `SubscriptionRenewed` - Renewal processed
- `SubscriptionCancelled` - Subscription ended
- `SubscriptionPaused` - Temporarily suspended

## Integration Points

- Payment processing
- Usage metering
- Provisioning systems
- Customer success