# Distribution

Multi-tier wholesale distribution.

## NAICS Code

**423000** - Merchant Wholesalers, Durable Goods

## Overview

This model manages wholesale distribution networks including distributor
relationships, territory management, and order routing.

## Key Entities

- **Distributor** - Distribution partner
- **Territory** - Geographic assignment
- **DistributionOrder** - Wholesale order

## Commands

- `OnboardDistributor` - Add distribution partner
- `AssignTerritory` - Define geographic coverage
- `PlaceOrder` - Create wholesale order
- `RouteOrder` - Determine fulfillment source
- `ConfirmDelivery` - Complete distribution

## Events

- `DistributorOnboarded` - Partner added
- `TerritoryAssigned` - Coverage defined
- `OrderPlaced` - Wholesale order created
- `OrderRouted` - Fulfillment determined
- `OrderDelivered` - Distribution complete

## Integration Points

- Warehouse management
- Transportation/logistics
- Pricing and contracts
- Accounts receivable