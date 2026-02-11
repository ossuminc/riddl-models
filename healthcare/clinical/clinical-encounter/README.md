# Clinical Encounter

Visit documentation and orders.

## NAICS Code

**621111** - Offices of Physicians

## Overview

This model manages clinical encounters including documentation, diagnoses,
orders, and treatment plans.

## Key Entities

- **Encounter** - Patient visit
- **Note** - Clinical documentation
- **Order** - Clinical directive

## Commands

- `StartEncounter` - Begin visit
- `DocumentNote` - Record findings
- `PlaceOrder` - Create directive
- `RecordDiagnosis` - Document condition
- `CloseEncounter` - End visit

## Events

- `EncounterStarted` - Visit began
- `NoteDocumented` - Findings recorded
- `OrderPlaced` - Directive created
- `DiagnosisRecorded` - Condition noted
- `EncounterClosed` - Visit ended

## Integration Points

- Scheduling
- Order management
- Billing/coding
- Care coordination