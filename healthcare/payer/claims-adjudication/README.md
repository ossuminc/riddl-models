# Claims Adjudication

Health claims processing and payment.

## NAICS Code

**524114** - Direct Health and Medical Insurance Carriers

## Overview

This model manages health claims from submission through payment including
validation, pricing, and payment determination.

## Key Entities

- **Claim** - Payment request
- **Adjudication** - Processing decision
- **Payment** - Reimbursement

## Commands

- `SubmitClaim` - Request payment
- `ValidateClaim` - Check completeness
- `PriceClaim` - Calculate payment
- `AdjudicateClaim` - Make decision
- `PayClaim` - Issue payment

## Events

- `ClaimSubmitted` - Request received
- `ClaimValidated` - Completeness checked
- `ClaimPriced` - Payment calculated
- `ClaimAdjudicated` - Decision made
- `ClaimPaid` - Payment issued

## Integration Points

- Provider networks
- Fee schedules
- Member enrollment
- Payment systems