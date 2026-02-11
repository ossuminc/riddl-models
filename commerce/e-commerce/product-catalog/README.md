# Product Catalog

Product listings, categories, and merchandising.

## NAICS Code

**454110** - Electronic Shopping and Mail-Order Houses

## Overview

This model manages the product catalog including product information,
categorization, pricing, images, and search optimization.

## Key Entities

- **Product** - Product master with attributes and variants
- **Category** - Hierarchical product categorization
- **PriceList** - Pricing tiers and promotions

## Commands

- `CreateProduct` - Add a new product
- `UpdateProduct` - Modify product details
- `SetPrice` - Update product pricing
- `AssignCategory` - Categorize a product
- `PublishProduct` - Make product visible

## Events

- `ProductCreated` - New product was added
- `ProductUpdated` - Product details changed
- `PriceChanged` - Product price was updated
- `ProductPublished` - Product is now visible
- `ProductRetired` - Product was discontinued

## Integration Points

- Inventory for availability
- Search engine for discovery
- Content management for images
- ERP for master data sync