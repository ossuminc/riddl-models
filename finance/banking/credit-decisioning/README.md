# Credit Decisioning

Risk scoring and credit limit determination.

## Overview

This model evaluates creditworthiness and determines appropriate credit
limits using automated decision logic.

## Key Entities

- **CreditRequest** - Request for credit
- **RiskScore** - Calculated risk assessment
- **Decision** - Approval or denial

## Commands

- `RequestCredit` - Submit for evaluation
- `CalculateScore` - Compute risk score
- `MakeDecision` - Determine outcome
- `OverrideDecision` - Manual intervention
- `RecordReason` - Document decision

## Events

- `CreditRequested` - Evaluation started
- `ScoreCalculated` - Risk computed
- `CreditApproved` - Request approved
- `CreditDenied` - Request denied
- `DecisionOverridden` - Manual change

## Integration Points

- Credit bureaus
- Fraud detection
- Regulatory compliance
- Adverse action notices