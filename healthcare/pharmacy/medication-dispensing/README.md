# Medication Dispensing Domain Model

This RIDDL domain model represents the complete medication dispensing workflow
in a pharmacy setting, from prescription receipt through patient pickup or
return to stock.

## Overview

The Medication Dispensing domain models the operational workflow of a retail
or hospital pharmacy's dispensing function. It captures the process of
converting a prescription order into a dispensed medication in the patient's
hands.

## Domain Structure

```
MedicationDispensing (domain)
├── Author: OssumInc
├── Users
│   ├── DispensingPharmacist - Licensed pharmacist for verification/counseling
│   ├── PharmacyTechnician - Certified technician for physical dispensing
│   └── PatientUser - Patient or authorized representative
├── Epic: DispensingWorkflow
│   ├── DrugSelectionCase - Select correct drug from inventory
│   ├── FillingCase - Physically dispense medication
│   ├── VerificationCase - Pharmacist verification
│   ├── LabelingCase - Print and apply prescription label
│   ├── CounselingCase - Patient consultation
│   └── PickupCase - Medication pickup transaction
├── DispensingContext (bounded context)
│   ├── Fill (entity) - Core aggregate for dispensing workflow
│   ├── FillRepository - Persistence for fill records
│   └── DispensingMetrics (projector) - Analytics and reporting
└── External Contexts
    ├── DrugDatabase - NDC codes, interactions, images
    ├── InventoryService - Stock levels, lot tracking
    ├── POSBilling - Copay collection
    ├── PrescriptionService - Source prescriptions
    └── PatientService - Patient information
```

## Fill Entity States

The Fill entity progresses through these states:

1. **PendingState** - Fill initiated, awaiting drug selection
2. **FillingState** - Drug selected, being filled and verified
3. **VerifiedState** - Pharmacist verified, ready for labeling
4. **ReadyState** - Labeled and staged for patient pickup
5. **DispensedState** - Successfully dispensed to patient

## Key Commands

| Command | Description |
|---------|-------------|
| InitiateFill | Start a new prescription fill |
| SelectDrug | Select drug product from inventory |
| FillPrescription | Complete physical fill process |
| VerifyFill | Pharmacist verification |
| PrintLabel | Generate and apply prescription label |
| CounselPatient | Record patient counseling |
| CompletePickup | Complete pickup transaction |
| ReturnToStock | Return unpicked medication to inventory |

## External Integrations

### DrugDatabase
Provides drug information including:
- NDC (National Drug Code) lookup
- Drug-drug interaction checking
- Drug images for visual verification

### InventoryService
Manages pharmacy inventory:
- Stock level tracking
- Lot number tracking for recalls
- Expiration monitoring
- Automatic reorder alerts

### POSBilling
Handles payment processing:
- Copay collection
- Multiple payment methods (card, HSA/FSA, cash)
- Payment failure handling
- Copay waiver processing

### PrescriptionService
Source system for prescriptions:
- Prescription details and directions
- Refill authorization
- Prescriber information

### PatientService
Patient information system:
- Patient demographics
- Allergy information
- Patient arrival notifications

## Metrics and Analytics

The DispensingMetrics projector tracks:

- **Fill Time Metrics** - Average time for each workflow stage
- **Counseling Compliance** - Rate of counseling provided vs. declined
- **Return Rates** - Percentage of fills returned to stock

## Validation

Validate this model with riddlc:

```bash
riddlc from medication-dispensing.conf validate
```

## Regulatory Considerations

This model supports pharmacy regulatory requirements including:
- Complete audit trail for all dispensing activities
- Pharmacist verification documentation
- Patient counseling documentation (OBRA '90)
- Lot tracking for recall management
- Signature capture for controlled substances
- Identity verification for pickup

## Related Patterns

This model demonstrates several DDD/Reactive patterns:
- Event-sourced entity (Fill)
- State machine with explicit states
- CQRS with projector for read-optimized views
- External context integration
