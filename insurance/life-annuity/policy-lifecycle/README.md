# Policy Lifecycle

Life insurance policy administration.

## NAICS Code

**524113** - Direct Life Insurance Carriers

## Overview

This model manages life insurance and annuity contracts from application
through claims including in-force servicing.

## Key Entities

- **Policy** - Life/annuity contract
- **Beneficiary** - Designated recipients
- **Transaction** - Policy change or payment

## Commands

- `SubmitApplication` - Start application
- `UnderwritePolicy` - Assess risk
- `IssuePolicy` - Create contract
- `ProcessChange` - Handle service request
- `FileClaim` - Submit death claim

## Events

- `ApplicationSubmitted` - Application received
- `PolicyIssued` - Contract created
- `BeneficiaryChanged` - Recipients updated
- `PremiumReceived` - Payment applied
- `ClaimFiled` - Death claim submitted

## Integration Points

- Underwriting systems
- Billing/collections
- Reinsurance
- Document management