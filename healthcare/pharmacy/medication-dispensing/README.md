# Medication Dispensing

Fill and dispense workflow.

## Overview

This model manages medication dispensing including drug selection, filling,
labeling, and patient pickup.

## Key Entities

- **Fill** - Dispensing action
- **Drug** - Selected medication
- **Label** - Patient instructions

## Commands

- `SelectDrug` - Choose medication
- `FillPrescription` - Dispense medication
- `PrintLabel` - Generate label
- `CounselPatient` - Provide guidance
- `CompletePickup` - Patient receives

## Events

- `DrugSelected` - Medication chosen
- `PrescriptionFilled` - Dispensed
- `LabelPrinted` - Label generated
- `PatientCounseled` - Guidance provided
- `PickupCompleted` - Patient received

## Integration Points

- Drug database
- Prescription management
- Inventory systems
- POS/billing