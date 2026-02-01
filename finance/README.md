# Financial Services

RIDDL models for banking, payments, and trading operations.

## Subsectors

### banking/
Core banking operations for retail and commercial accounts.

**Models:**
- `account-management/` - Open, close, maintain accounts
- `fund-transfer/` - ACH, wire, internal transfers
- `loan-origination/` - Application through disbursement
- `credit-decisioning/` - Scoring, underwriting, limits

### payments/
Payment processing and digital money movement.

**Models:**
- `payment-processing/` - Authorization, capture, settlement
- `digital-wallet/` - Balance, transfers, spending
- `merchant-acquiring/` - Onboarding, settlement, chargebacks

### trading/
Securities trading and settlement.

**Models:**
- `order-management/` - Order routing, execution
- `trade-settlement/` - Clearing, settlement, custody

## Common Patterns

Financial models frequently use:
- Event sourcing for complete transaction history
- Saga patterns for multi-party transactions (transfers, settlements)
- Strong invariants for balance constraints
- Projectors for real-time balance views

## Compliance Considerations

Financial models should include:
- Audit trail for all state changes
- Idempotency for payment operations
- Compensation logic for failed transactions