# Fund Management

VC fund operations and LP management.

## NAICS Code

**523910** - Miscellaneous Intermediation

## Overview

This model manages venture capital fund operations including fund
creation, LP commitment tracking, capital calls, distributions,
management fees, NAV updates, and fund lifecycle through harvest
period and closure.

## Key Entities

- **Fund** - VC fund with LP commitments and performance metrics
- **LPCommitment** - Limited partner capital commitment
- **CapitalCall** - Request for LP capital contribution
- **Distribution** - Return of capital and gains to LPs

## Commands

- `CreateFund` - Create a new VC fund
- `AddLPCommitment` - Record LP commitment
- `RecordFirstClose` - Record first close
- `RecordFinalClose` - Record final close
- `IssueCapitalCall` - Issue capital call to LPs
- `RecordCallPayment` - Record LP call payment
- `IssueDistribution` - Distribute proceeds to LPs
- `ChargeManagementFee` - Charge periodic management fee
- `UpdateNAV` - Update fund net asset value
- `StartHarvestPeriod` - Transition to harvest period
- `CloseFund` - Close the fund

## Events

- `FundCreated` - Fund initialized
- `LPCommitmentAdded` - LP committed capital
- `FirstCloseRecorded` - First close completed
- `FinalCloseRecorded` - Final close completed
- `CapitalCallIssued` - Capital call sent
- `CallPaymentReceived` - LP payment received
- `DistributionIssued` - Distribution sent
- `ManagementFeeCharged` - Fee charged
- `NAVUpdated` - NAV recalculated
- `HarvestPeriodStarted` - Investment period ended
- `FundClosed` - Fund terminated

## Integration Points

- LP portal for communications
- Fund accounting system
- Banking services for wire transfers
- Compliance reporting
