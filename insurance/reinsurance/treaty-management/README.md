# Treaty Management

Reinsurance contract administration.

## Overview

This model manages reinsurance treaties including placement, cession
calculations, and bordereaux reporting.

## Key Entities

- **Treaty** - Reinsurance agreement
- **Cession** - Risk transfer
- **Bordereaux** - Periodic reporting

## Commands

- `NegotiateTreaty` - Draft agreement
- `ExecuteTreaty` - Finalize contract
- `CalculateCession` - Compute shares
- `SubmitBordereaux` - Report activity
- `RenewTreaty` - Process renewal

## Events

- `TreatyNegotiated` - Draft created
- `TreatyExecuted` - Contract signed
- `CessionCalculated` - Shares computed
- `BordereauxSubmitted` - Report sent
- `TreatyRenewed` - Renewal processed

## Integration Points

- Policy administration
- Claims systems
- Accounting
- Regulatory reporting