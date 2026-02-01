# Claims Processing

P&C claims handling and settlement.

## Overview

This model manages insurance claims from first notice through settlement
including investigation, adjustment, and payment.

## Key Entities

- **Claim** - Loss notice and file
- **Investigation** - Claim validation
- **Payment** - Settlement disbursement

## Commands

- `ReportClaim` - Submit FNOL
- `AssignAdjuster` - Route claim
- `InvestigateClaim` - Validate loss
- `ApproveClaim` - Authorize payment
- `PayClaim` - Disburse funds

## Events

- `ClaimReported` - FNOL received
- `AdjusterAssigned` - Claim routed
- `InvestigationComplete` - Validation done
- `ClaimApproved` - Payment authorized
- `ClaimPaid` - Funds disbursed

## Integration Points

- Policy administration
- Vendor networks
- Payment systems
- Subrogation