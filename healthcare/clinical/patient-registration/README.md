# Patient Registration

Patient demographics and intake.

## Overview

This model manages patient registration including demographics, insurance
verification, and consent documentation.

## Key Entities

- **Patient** - Individual receiving care
- **Insurance** - Coverage information
- **Consent** - Authorization documents

## Commands

- `RegisterPatient` - Create patient record
- `UpdateDemographics` - Modify patient info
- `VerifyInsurance` - Check coverage
- `RecordConsent` - Document authorization
- `MergePatients` - Combine duplicates

## Events

- `PatientRegistered` - Record created
- `DemographicsUpdated` - Info modified
- `InsuranceVerified` - Coverage confirmed
- `ConsentRecorded` - Authorization documented
- `PatientsMerged` - Duplicates combined

## Integration Points

- Scheduling systems
- Insurance eligibility
- Master patient index
- EHR systems