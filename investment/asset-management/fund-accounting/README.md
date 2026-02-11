# Fund Accounting

Investment fund NAV calculation, transaction processing, and
regulatory reporting.

## NAICS Code

**523920** - Portfolio Management and Investment Advice

## Overview

This model manages investment fund accounting operations including
daily NAV calculations, security transaction recording, portfolio
holding management, investor subscriptions and redemptions, fund
suspension and resumption, and regulatory reporting.

## Key Entities

- **Fund** - Investment fund with holdings and investor accounts
- **NAVRecord** - Daily net asset value calculation
- **TransactionRecord** - Security buy/sell and income transactions
- **HoldingRecord** - Portfolio position with cost basis and value
- **InvestorAccount** - Investor share balance and account value

## Commands

- `CreateFund` - Initialize a new fund
- `CalculateNAV` - Calculate daily net asset value
- `RecordTransaction` - Record a fund transaction
- `UpdateHolding` - Update portfolio holding position
- `ProcessSubscription` - Process investor subscription
- `ProcessRedemption` - Process investor redemption
- `SuspendFund` - Suspend fund operations
- `ResumeFund` - Resume suspended operations

## Events

- `FundCreated` - Fund initialized
- `NAVCalculated` - NAV computation completed
- `TransactionRecorded` - Transaction recorded
- `HoldingUpdated` - Position updated
- `SubscriptionProcessed` - Investor shares issued
- `RedemptionProcessed` - Investor shares redeemed
- `FundSuspended` - Operations halted
- `FundResumed` - Operations resumed

## Integration Points

- Market data providers
- Custodian services
- Transfer agent
- Compliance monitoring
