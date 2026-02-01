# Policy Administration

P&C policy lifecycle management.

## Overview

This model manages insurance policies from quote through renewal including
endorsements, cancellations, and reinstatements.

## Key Entities

- **Policy** - Insurance contract
- **Coverage** - Insured perils
- **Endorsement** - Policy modification

## Commands

- `QuotePolicy` - Generate quote
- `BindPolicy` - Issue policy
- `EndorsePolicy` - Modify coverage
- `CancelPolicy` - Terminate policy
- `RenewPolicy` - Process renewal

## Events

- `QuoteGenerated` - Quote created
- `PolicyBound` - Policy issued
- `PolicyEndorsed` - Coverage modified
- `PolicyCancelled` - Policy terminated
- `PolicyRenewed` - Renewal processed

## Integration Points

- Rating engine
- Document generation
- Billing systems
- Reinsurance