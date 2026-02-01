# Digital Wallet

Stored value and P2P payments.

## Overview

This model manages digital wallet balances, funding sources, and
peer-to-peer transfers.

## Key Entities

- **Wallet** - Stored value balance
- **FundingSource** - Linked payment method
- **Transfer** - P2P money movement

## Commands

- `CreateWallet` - Open wallet
- `AddFundingSource` - Link payment method
- `LoadWallet` - Add funds
- `SendMoney` - P2P transfer
- `WithdrawFunds` - Cash out

## Events

- `WalletCreated` - Wallet opened
- `FundingSourceAdded` - Method linked
- `WalletLoaded` - Funds added
- `MoneySent` - P2P completed
- `FundsWithdrawn` - Cash out done

## Integration Points

- Bank accounts
- Card networks
- Identity verification
- Compliance screening