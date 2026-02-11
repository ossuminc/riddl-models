# Hospital Supply Chain

A RIDDL domain model for hospital medical supply procurement, inventory
management, and distribution.

## NAICS Code

**622110** - General Medical and Surgical Hospitals

## Overview

This model covers the end-to-end flow of medical supplies from vendors through
central stores to clinical departments. It handles:

- **Procurement**: Requisition, approval, ordering, and receiving
- **Inventory Management**: Stock levels, par levels, adjustments
- **Distribution**: Issuing supplies to clinical departments
- **Analytics**: Usage trends, vendor performance, demand forecasting

## Domain Structure

```
HospitalSupplyChain (Domain)
├── Users
│   ├── MaterialsManager - oversees supply chain operations
│   ├── Buyer - handles purchasing and vendor relations
│   ├── StoreKeeper - manages physical inventory
│   └── DepartmentUser - requests and consumes supplies
│
├── Epic: MedicalSupplyManagement
│   ├── RequisitionToReceipt - procurement workflow
│   ├── SupplyDistribution - internal distribution
│   └── InventoryManagement - accuracy and optimization
│
└── SupplyContext (Bounded Context)
    ├── SupplyOrder (Entity) - order lifecycle management
    ├── SupplyRepository - data persistence
    └── Projectors
        ├── StockLevelProjector - current inventory
        ├── UsageTrendProjector - consumption patterns
        └── VendorPerformanceProjector - vendor metrics
```

## External Integrations

The model integrates with three external systems:

| Context | Purpose |
|---------|---------|
| VendorCatalog | Product catalogs, pricing, availability |
| FinanceAP | Invoice processing, three-way matching, payments |
| ClinicalUsage | Procedure-based consumption, case carts |

## Order Lifecycle States

```
Requisitioned → Approved → Ordered → Received → Completed
      ↓                         ↓
  Cancelled             PartiallyReceived
```

1. **Requisitioned**: Initial request awaiting approval
2. **Approved**: Authorized for purchase
3. **Ordered**: Sent to vendor
4. **PartiallyReceived**: Some items received
5. **Received**: All items received, awaiting put-away
6. **Completed**: Items in inventory

## Key Commands and Events

| Command | Event | Description |
|---------|-------|-------------|
| CreateRequisition | RequisitionCreated | Initiate supply request |
| ApproveRequisition | RequisitionApproved | Authorize for purchase |
| PlaceOrder | OrderPlaced | Send order to vendor |
| ReceiveShipment | ShipmentReceived | Record incoming delivery |
| PutAway | ItemsPutAway | Place in storage locations |
| IssueSupplies | SuppliesIssued | Distribute to departments |
| AdjustInventory | InventoryAdjusted | Correct inventory counts |
| SetParLevel | ParLevelSet | Configure reorder parameters |

## Validation

```bash
cd /path/to/riddl-models/healthcare/hospitals/supply-chain
riddlc from supply-chain.conf validate
```

## Related Models

- `healthcare/hospitals/patient-flow/` - Patient admission and discharge
- `healthcare/hospitals/clinical-orders/` - Medical order management
- `logistics/warehousing/` - General warehouse operations

## Author

Ossum Inc. (support@ossuminc.com)
