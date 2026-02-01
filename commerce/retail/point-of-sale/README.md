# Point of Sale

In-store transaction processing.

## Overview

This model handles retail checkout transactions including item scanning,
payment processing, receipts, and end-of-day reconciliation.

## Key Entities

- **Transaction** - Sales transaction with line items
- **Register** - POS terminal state and drawer
- **Tender** - Payment method applied

## Commands

- `StartTransaction` - Open new sale
- `ScanItem` - Add product to sale
- `ApplyDiscount` - Apply promotion or markdown
- `ProcessPayment` - Complete tender
- `VoidTransaction` - Cancel entire sale

## Events

- `TransactionStarted` - New sale opened
- `ItemScanned` - Product added
- `PaymentProcessed` - Tender completed
- `TransactionCompleted` - Sale finalized
- `TransactionVoided` - Sale was cancelled

## Integration Points

- Inventory for stock updates
- Payment terminals
- Receipt printers
- Loyalty programs