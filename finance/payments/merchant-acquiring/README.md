# Merchant Acquiring

Merchant onboarding and settlement.

## NAICS Code

**522320** - Financial Transactions Processing

## Overview

This model manages merchant relationships from onboarding through
ongoing settlement and statement generation.

## Key Entities

- **Merchant** - Business accepting payments
- **MerchantAccount** - Processing agreement
- **Settlement** - Funds disbursement

## Commands

- `OnboardMerchant` - Start signup
- `UnderwriteMerchant` - Assess risk
- `ActivateMerchant` - Enable processing
- `SettleFunds` - Disburse funds
- `HoldFunds` - Reserve for disputes

## Events

- `MerchantOnboarded` - Signup started
- `MerchantApproved` - Underwriting passed
- `MerchantActivated` - Ready to process
- `SettlementCompleted` - Funds disbursed
- `FundsHeld` - Reserve created

## Integration Points

- Credit underwriting
- Bank accounts
- Payment processing
- Dispute management