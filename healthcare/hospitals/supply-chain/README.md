# Hospital Supply Chain

Medical supplies and inventory.

## Overview

This model manages hospital supplies including procurement, inventory
management, and par level maintenance.

## Key Entities

- **Item** - Supply item
- **Inventory** - Stock on hand
- **Order** - Purchase request

## Commands

- `OrderSupplies` - Request items
- `ReceiveShipment` - Process delivery
- `IssueItems` - Dispense supplies
- `AdjustInventory` - Correct counts
- `SetParLevel` - Define targets

## Events

- `SuppliesOrdered` - Items requested
- `ShipmentReceived` - Delivery processed
- `ItemsIssued` - Supplies dispensed
- `InventoryAdjusted` - Counts corrected
- `ParLevelSet` - Targets defined

## Integration Points

- Procurement systems
- Vendor catalogs
- Finance/AP
- Usage analytics