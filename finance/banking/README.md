E# Banking

Core banking operations and financial account management.

## Scope

This subsector covers traditional banking operations and modern digital
banking, including:

- Deposit and savings account management
- Loan origination and servicing
- Credit decisioning and risk assessment
- Fund transfers and payments
- Regulatory compliance (KYC, AML)

## Models

| Model | Description |
|-------|-------------|
| `account-management/` | Customer accounts, balances, and transactions |
| `loan-origination/` | Loan application, underwriting, and approval |
| `credit-decisioning/` | Risk scoring and credit limit determination |
| `fund-transfer/` | Internal and external money movement |

## Related Patterns

- `patterns/entity/event-sourced/` - For transaction audit trails
- `patterns/saga/distributed-transaction/` - For multi-step transfers