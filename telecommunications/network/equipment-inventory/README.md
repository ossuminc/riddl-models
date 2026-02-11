# Equipment Inventory

Network equipment inventory and lifecycle management for telecommunications
providers.

## NAICS Code

**517311** - Wired Telecommunications Carriers

## Overview

This domain model covers the complete lifecycle of network equipment from
procurement through disposal, including warehouse management, site
installation, maintenance tracking, and firmware management.

## Key Concepts

- **EquipmentItem** - Individual piece of network equipment (router, switch,
  antenna, etc.) tracked through its full lifecycle
- **InventoryContext** - Bounded context managing equipment registration,
  allocation, installation, maintenance, and decommissioning
- **ProcurementSystem** - External system for vendor purchase orders
- **NetworkManagementSystem** - External NMS for registering installed
  equipment as network elements

## Equipment Lifecycle

```
Ordered → InTransit → Received → InWarehouse → Allocated → Installed →
InService → Maintenance (loop) → Decommissioned → Disposed
```

## Validation

```bash
riddlc from equipment-inventory.conf validate
```
