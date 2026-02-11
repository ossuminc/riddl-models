# Account Management

Customer banking accounts and transactions.

## NAICS Code

**522110** - Commercial Banking

## Overview

This model manages deposit accounts, balances, and transaction history for
retail and commercial banking.

## Key Entities

- **Account** - Bank account with balance
- **Transaction** - Credit or debit entry
- **Statement** - Periodic account summary

## Commands

- `OpenAccount` - Create new account
- `CloseAccount` - Close account
- `PostTransaction` - Record entry
- `PlaceHold` - Restrict funds
- `GenerateStatement` - Create statement

## Events

- `AccountOpened` - New account created
- `AccountClosed` - Account closed
- `TransactionPosted` - Entry recorded
- `BalanceUpdated` - Balance changed
- `StatementGenerated` - Statement ready

## Integration Points

- Core banking system
- Card processing
- AML/KYC systems
- Regulatory reporting