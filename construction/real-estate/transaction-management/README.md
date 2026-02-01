# Transaction Management

Real estate listings, offers, and closings.

## Scope

This model covers real estate transaction operations, including:

- Property listing and marketing
- Offer negotiation and acceptance
- Due diligence and inspections
- Escrow and title coordination
- Closing and settlement

## Key Concepts

| Concept | Description |
|---------|-------------|
| Listing | A property offered for sale |
| Offer | A buyer's proposal with terms |
| Escrow | Funds held pending closing |
| Closing | The final transfer of ownership |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For closing workflow
- `patterns/workflow/process-manager/` - For due diligence
