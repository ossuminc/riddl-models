# Payment Processing

Transaction authorization and capture.

## Overview

This model handles payment transactions from authorization through
settlement including card, ACH, and alternative methods.

## Key Entities

- **Transaction** - Payment attempt
- **Authorization** - Approval to charge
- **Capture** - Settlement request

## Commands

- `AuthorizePayment` - Request approval
- `CapturePayment` - Request settlement
- `VoidPayment` - Cancel authorization
- `RefundPayment` - Return funds
- `ChargebackPayment` - Process dispute

## Events

- `PaymentAuthorized` - Approval received
- `PaymentCaptured` - Settlement requested
- `PaymentVoided` - Authorization cancelled
- `PaymentRefunded` - Funds returned
- `ChargebackReceived` - Dispute filed

## Integration Points

- Card networks (Visa, MC)
- Payment gateways
- Fraud detection
- Reconciliation systems