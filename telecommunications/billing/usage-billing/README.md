# Usage Billing

Metered usage collection, rating, and invoice generation for
telecommunications services.

## NAICS Code

**517311** - Wired Telecommunications Carriers

## Scope

This model covers usage billing operations, including:

- Billing account creation and management
- Usage record collection from network elements
- Rate plan management and plan changes
- Invoice generation and delivery
- Payment processing and credit adjustments
- Account suspension and reactivation
- Dispute resolution workflows

## Key Concepts

| Concept | Description |
|---------|-------------|
| BillingAccount | Customer account with rate plan and balance |
| UsageRecord | Metered usage event (voice, data, SMS) |
| RatePlan | Pricing structure with rates and allowances |
| Invoice | Period bill with line items and taxes |
| PaymentRecord | Payment applied against an invoice |

## Related Patterns

- `patterns/entity/event-sourced/` - For billing audit trail
- `patterns/projection/read-model/` - For account summaries
