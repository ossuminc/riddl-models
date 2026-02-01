# Deal Flow

VC opportunity pipeline management.

## Overview

This model manages the venture capital deal pipeline from sourcing through
investment decision including screening and due diligence.

## Key Entities

- **Opportunity** - Potential investment
- **Screening** - Initial evaluation
- **DueDiligence** - Deep investigation

## Commands

- `SourceDeal` - Add opportunity
- `ScreenOpportunity` - Initial review
- `StartDueDiligence` - Begin investigation
- `PresentToIC` - Investment committee
- `MakeInvestment` - Execute deal

## Events

- `DealSourced` - Opportunity added
- `ScreeningComplete` - Initial review done
- `DueDiligenceComplete` - Investigation done
- `ICDecisionMade` - Committee decision
- `InvestmentMade` - Deal executed

## Integration Points

- CRM systems
- Document management
- Portfolio management
- Fund administration