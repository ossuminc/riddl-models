# riddl-models

A library of RIDDL models organized by industry sector, plus reusable patterns
for domain-driven design with RIDDL.

## What is RIDDL?

[RIDDL](https://github.com/ossuminc/riddl) (Reactive Interface to Domain
Definition Language) is a domain-specific language for defining event-driven
systems using Domain-Driven Design principles.

## Repository Structure

```
riddl-models/
├── patterns/           # Reusable DDD/Reactive patterns
├── technology/         # SaaS, DevOps, Platform services
├── investment/         # VC, Private Equity, Asset Management
├── finance/            # Banking, Payments, Trading
├── insurance/          # P&C, Life, Reinsurance
├── commerce/           # E-commerce, Retail, Marketplace
├── hospitality/        # Hotels, Restaurants, Travel
├── entertainment/      # Media, Gaming, Sports
├── marketing/          # Campaigns, Advertising, Analytics
├── healthcare/         # Clinical, Pharmacy, Payer
├── manufacturing/      # Discrete, Process, Maintenance
├── construction/       # Projects, Real Estate
├── engineering/        # PLM, Consulting
├── transportation/     # Freight, Passenger, Fleet
├── logistics/          # Warehousing, Fulfillment
├── natural-resources/  # Mining, Oil & Gas, Agriculture
├── utilities/          # Electric, Gas, Water
├── telecommunications/ # Network, Billing
├── government/         # Citizen Services, Public Safety
├── education/          # Academic, Training
└── professional-services/ # Legal, Accounting, HR
```

## Quick Start

### Using a Model

1. Browse to a sector directory (e.g., `commerce/e-commerce/`)
2. Find a model that fits your needs
3. Copy the `.riddl` file as a starting point
4. Customize types, commands, and events for your domain

### Using a Pattern

1. Browse `patterns/` for available patterns
2. Read the pattern's README for usage guidance
3. Copy the template and replace `{Placeholders}`
4. Integrate into your domain model

## Model Complexity Tiers

Models may include a complexity tier in their metadata:

| Tier | Best For |
|------|----------|
| `starter` | Small businesses, MVPs, learning |
| `standard` | Mid-market, full-featured |
| `enterprise` | Large organizations, compliance-heavy |

## Example: Shopping Cart

```riddl
// From commerce/e-commerce/shopping-cart/

domain ECommerce is {
  context ShoppingCart is {
    entity Cart is {
      briefly "Customer's shopping cart"

      type CartId is Id(Cart)
      type CartItem is { productId: ProductId, quantity: Integer, price: Decimal }

      command AddItem is { cartId: CartId, item: CartItem }
      command RemoveItem is { cartId: CartId, productId: ProductId }
      command Checkout is { cartId: CartId }

      event ItemAdded is { cartId: CartId, item: CartItem }
      event ItemRemoved is { cartId: CartId, productId: ProductId }
      event CartCheckedOut is { cartId: CartId, total: Decimal }

      state Active is {
        id: CartId,
        items: CartItem*,
        total: Decimal
      }

      handler CartHandler is {
        on command AddItem {
          set field items to state.items + @AddItem.item
          send event ItemAdded to outlet Events
        }
        on command Checkout {
          send event CartCheckedOut to outlet Events
        }
      }
    }
  }
}
```

## Available Patterns

| Pattern | Use Case |
|---------|----------|
| Event-Sourced Entity | Full audit trail, temporal queries |
| Aggregate Root | Parent-child entity relationships |
| Saga | Multi-step distributed transactions |
| Repository | Entity persistence abstraction |
| Projector | CQRS read-optimized views |
| Process Manager | Event-driven workflow coordination |

## Integration

These models work with:

- **[riddl](https://github.com/ossuminc/riddl)** - Compiler and validation
- **[riddl-mcp-server](https://github.com/ossuminc/riddl-mcp-server)** - AI
  assistance for RIDDL development
- **[riddlsim](https://github.com/ossuminc/riddlsim)** - Model simulation
- **[synapify](https://github.com/ossuminc/synapify)** - Visual RIDDL editor

## Contributing

1. Fork the repository
2. Create your model in the appropriate sector
3. Include a README.md explaining the model
4. Optionally add a `.metadata.json` file
5. Submit a pull request

See [CLAUDE.md](CLAUDE.md) for detailed contribution guidelines.

## License

Apache 2.0 - See [LICENSE](LICENSE)