# Trade Credit

B2B payment terms and credit management.

## NAICS Code

**423000** - Merchant Wholesalers, Durable Goods

## Overview

This model manages trade credit for business customers including credit
limits, payment terms, and collections.

## Key Entities

- **CreditAccount** - Customer credit profile
- **CreditLimit** - Approved credit amount
- **Invoice** - Accounts receivable

## Commands

- `RequestCredit` - Apply for trade credit
- `ApproveCredit` - Grant credit limit
- `ExtendTerms` - Adjust payment terms
- `RecordPayment` - Apply payment
- `InitiateCollection` - Start collections

## Events

- `CreditRequested` - Application submitted
- `CreditApproved` - Credit was granted
- `CreditDenied` - Application rejected
- `PaymentReceived` - Payment applied
- `AccountDelinquent` - Past due

## Integration Points

- Credit bureaus
- Accounts receivable
- Collections agencies
- Risk management