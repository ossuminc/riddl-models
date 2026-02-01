# Prescription Management

Rx intake and refill processing.

## Overview

This model manages prescriptions including intake, verification, refill
processing, and transfer handling.

## Key Entities

- **Prescription** - Medication order
- **Refill** - Renewal request
- **Transfer** - Pharmacy change

## Commands

- `ReceivePrescription` - Accept new Rx
- `VerifyPrescription` - Validate order
- `ProcessRefill` - Handle renewal
- `TransferPrescription` - Move to pharmacy
- `SuspendPrescription` - Hold processing

## Events

- `PrescriptionReceived` - Rx accepted
- `PrescriptionVerified` - Order validated
- `RefillProcessed` - Renewal handled
- `PrescriptionTransferred` - Moved
- `PrescriptionSuspended` - Processing held

## Integration Points

- E-prescribing networks
- Prescriber verification
- Insurance systems
- Dispensing workflow