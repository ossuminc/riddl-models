# Trade Settlement

Post-trade clearing and settlement.

## NAICS Code

**523150** - Investment Banking and Securities Intermediation

## Overview

This model handles post-trade processing including confirmation, clearing,
and settlement of securities transactions.

## Key Entities

- **Trade** - Matched transaction
- **Confirmation** - Trade agreement
- **Settlement** - Final exchange

## Commands

- `MatchTrade` - Confirm counterparty
- `AffirmTrade` - Agree to terms
- `AllocateTrade` - Assign to accounts
- `NetPositions` - Calculate net obligations
- `SettleTrade` - Exchange securities/cash

## Events

- `TradeMatched` - Counterparty confirmed
- `TradeAffirmed` - Terms agreed
- `TradeAllocated` - Accounts assigned
- `PositionsNetted` - Obligations calculated
- `TradeSettled` - Exchange completed

## Integration Points

- Clearing houses
- Custodians
- Position keeping
- Fails management