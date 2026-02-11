# Fund Transfer

Money movement between accounts.

## NAICS Code

**522110** - Commercial Banking

## Overview

This model handles internal and external fund transfers including ACH,
wire transfers, and real-time payments.

## Key Entities

- **Transfer** - Money movement request
- **TransferLeg** - Debit or credit leg
- **Settlement** - Final posting

## Commands

- `InitiateTransfer` - Start transfer
- `ValidateTransfer` - Check feasibility
- `ExecuteTransfer` - Process movement
- `CancelTransfer` - Stop pending transfer
- `ReverseTransfer` - Undo completed transfer

## Events

- `TransferInitiated` - Request submitted
- `TransferValidated` - Checks passed
- `TransferExecuted` - Funds moved
- `TransferCompleted` - Settlement done
- `TransferFailed` - Transfer failed

## Integration Points

- Payment networks (ACH, SWIFT)
- Core banking
- Fraud detection
- Compliance screening