# Reactive BBQ

A comprehensive RIDDL domain model for a 500+ location BBQ restaurant
chain, demonstrating reactive, event-driven bounded context isolation
to solve real architectural problems.

## NAICS Code

722511 — Full-Service Restaurants

## Overview

Reactive BBQ (RBBQ) models a restaurant chain suffering from:

- **Peak-hour performance degradation** from synchronous, tightly
  coupled systems
- **Cascading failures** where one component brings down others
- **Deployment downtime** from monolithic releases
- **Blocked strategic initiatives** (loyalty program, electronic
  menus, kitchen display screens)

The model demonstrates how reactive architecture with bounded context
isolation addresses every stakeholder concern.

## Architecture

### 3 Domains, 11 Bounded Contexts, 13 Entities

**Restaurant Domain** (customer-facing operations):

| Context | Entities | Purpose |
|---------|----------|---------|
| FrontOfHouse | Reservation, TableOrder | Seating, orders, payment |
| Kitchen | KitchenTicket | Digital ticket queue, station mgmt |
| Bar | DrinkOrder | Drink prep, server notifications |
| OnlineOrdering | OnlineOrder | Menu, cart, checkout |
| Delivery | Delivery | Driver dispatch, GPS tracking |
| Loyalty | LoyaltyAccount | Points accrual and redemption |

**BackOffice Domain** (internal operations):

| Context | Entities | Purpose |
|---------|----------|---------|
| Scheduling | Shift | Staff shifts, time tracking |
| Inventory | InventoryItem | Stock levels, reordering |
| Reporting | *(projectors only)* | Sales, labor, inventory reports |

**Corporate Domain** (chain-wide management):

| Context | Entities | Purpose |
|---------|----------|---------|
| MenuManagement | MenuItem, MenuRelease | Recipe dev, atomic menu distribution |
| SupplyChain | PurchaseOrder | Vendor mgmt, bulk ordering |
| Marketing | Campaign | Promotions and campaigns |

### How CEO Concerns Are Addressed

| Concern | Solution | RIDDL Construct |
|---------|----------|-----------------|
| Peak-hour performance | Async event-driven, no blocking | Message-driven handlers |
| Cascading failures | Context isolation | 11 independent contexts |
| Deployment downtime | Independent deployability | Separate contexts |
| Loyalty program blocked | Isolated Loyalty context | Own context + adaptors |
| Electronic menus blocked | OnlineOrdering decoupled from Delivery | Separate contexts |
| Kitchen displays blocked | Kitchen with KitchenDisplay projector | Projector + events |
| Reports degrade perf | Reporting in separate context | CQRS projectors |

### Cross-Context Communication

Contexts communicate through adaptors, maintaining loose coupling:

- FrontOfHouse → Kitchen (food orders)
- FrontOfHouse → Bar (drink orders)
- FrontOfHouse → Loyalty (payment → points)
- OnlineOrdering → Kitchen (online orders)
- OnlineOrdering → Delivery (delivery fulfillment)
- OnlineOrdering → Loyalty (online payment → points)
- Kitchen → Inventory (stock consumption)
- MenuManagement → FrontOfHouse (menu distribution)

## Validation

```bash
# From the repository root
sbt compile

# Or manually
riddlc from reactive-bbq.conf validate
```

## Key Design Decisions

1. **OnlineOrdering is separate from Delivery** — enables electronic
   menus without coupling to delivery operations
2. **Loyalty is its own context** — can be developed and rolled out
   independently without touching other systems
3. **Reporting uses CQRS projectors** — report generation never
   impacts production performance
4. **Kitchen uses event sourcing** — tickets survive crashes, no
   more lost orders
5. **MenuRelease provides atomic distribution** — menu updates go
   to all 500+ locations simultaneously

## Stakeholder Personas

- **CEO** — Strategic initiatives and chain-wide performance
- **Corporate Head Chef** — Recipe development and menu coordination
- **Host** — Reservation and seating management
- **Server** — Table service and payment processing
- **Bartender** — Drink preparation and notifications
- **Chef** — Kitchen ticket queue and quality control
- **Cook** — Food preparation at stations
- **Delivery Driver** — Order delivery with offline resilience
- **Online Customer** — Website/app ordering experience
