# Payments

Payment processing, digital wallets, and merchant services.

## Scope

This subsector covers the movement of money between parties in commercial
transactions, including:

- Card payment processing
- Digital wallet and stored value
- Merchant acquiring and settlement
- Payment gateway integration
- Fraud detection and prevention

## Models

| Model | Description |
|-------|-------------|
| `payment-processing/` | Transaction authorization and capture |
| `digital-wallet/` | Stored value, funding sources, and P2P transfers |
| `merchant-acquiring/` | Merchant onboarding and settlement |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For payment authorization flows
- `patterns/entity/event-sourced/` - For transaction history