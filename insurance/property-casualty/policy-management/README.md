# Policy Management

P&C insurance policy lifecycle and administration.

## NAICS Code

**524126** - Direct Property and Casualty Insurance Carriers

## Overview

This model manages insurance policies from issuance through renewal
including binding, endorsements, suspensions, reinstatements,
cancellations, and non-renewals.

## Key Entities

- **Policy** - Insurance contract with coverages and premiums
- **InsuredProperty** - Property being covered
- **EndorsementInfo** - Mid-term policy modification

## Commands

- `IssuePolicy` - Issue new policy
- `BindPolicy` - Bind coverage with payment frequency
- `AddEndorsement` - Add policy endorsement
- `ProcessRenewal` - Offer renewal terms
- `AcceptRenewal` - Accept renewal offer
- `SuspendPolicy` - Suspend coverage
- `ReinstatePolicy` - Reinstate suspended policy
- `CancelPolicy` - Cancel policy
- `NonRenewPolicy` - Non-renew at expiration

## Events

- `PolicyIssued` - Policy created
- `PolicyBound` - Coverage bound
- `EndorsementAdded` - Coverage modified
- `RenewalOffered` - Renewal terms presented
- `RenewalAccepted` - Renewal confirmed
- `PolicySuspended` - Coverage suspended
- `PolicyReinstated` - Coverage restored
- `PolicyCancelled` - Policy terminated
- `PolicyNonRenewed` - Policy not renewed

## Integration Points

- Rating engine
- Underwriting service
- Document generation
- Billing systems
- Agency management
- Regulatory reporting
