# Inventory Management

Store-level stock management.

## NAICS Code

**452000** - General Merchandise Retailers

## Overview

This model tracks inventory at the store level including receiving, stock
levels, cycle counts, and inter-store transfers.

## Key Entities

- **StockItem** - Product quantity at location
- **Receipt** - Inbound shipment receiving
- **Transfer** - Inter-location movement

## Commands

- `ReceiveShipment` - Process inbound goods
- `AdjustStock` - Manual quantity correction
- `RequestTransfer` - Initiate inter-store move
- `CompleteCount` - Record cycle count
- `WriteOff` - Remove damaged/lost items

## Events

- `ShipmentReceived` - Goods were received
- `StockAdjusted` - Quantity was corrected
- `TransferCompleted` - Items moved locations
- `CountRecorded` - Cycle count finished
- `StockWrittenOff` - Items removed

## Integration Points

- Warehouse management
- Purchase orders
- Sales transactions
- Reporting systems