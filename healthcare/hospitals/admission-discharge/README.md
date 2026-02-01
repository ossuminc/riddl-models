# Admission, Discharge, Transfer

Patient flow and bed management.

## Overview

This model manages inpatient flow including admissions, transfers between
units, discharges, and bed assignment.

## Key Entities

- **Admission** - Inpatient stay
- **Bed** - Physical location
- **Transfer** - Unit movement

## Commands

- `AdmitPatient` - Start inpatient stay
- `AssignBed` - Place patient
- `TransferPatient` - Move to unit
- `DischargePatient` - End stay
- `PlannedDischarge` - Schedule departure

## Events

- `PatientAdmitted` - Stay started
- `BedAssigned` - Patient placed
- `PatientTransferred` - Unit changed
- `PatientDischarged` - Stay ended
- `DischargePlanned` - Departure scheduled

## Integration Points

- Bed management
- Nursing workflow
- Case management
- Environmental services