# Fund Administration

VC fund operations and LP reporting.

## Overview

This model manages fund administration including capital calls,
distributions, NAV calculations, and LP communications.

## Key Entities

- **Fund** - Investment vehicle
- **CapitalCall** - LP funding request
- **Distribution** - Return of capital/gains

## Commands

- `IssueCapitalCall` - Request funds
- `RecordContribution` - Track receipt
- `CalculateNAV` - Compute value
- `IssueDistribution` - Return funds
- `GenerateReport` - LP reporting

## Events

- `CapitalCallIssued` - Funds requested
- `ContributionReceived` - Payment received
- `NAVCalculated` - Value computed
- `DistributionIssued` - Funds returned
- `ReportGenerated` - Report sent

## Integration Points

- Banking systems
- Accounting
- Portfolio management
- Investor portal