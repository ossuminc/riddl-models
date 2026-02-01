# Clinical Trials

Study management and data collection.

## Overview

This model manages clinical trials including study design, site management,
subject enrollment, and data collection.

## Key Entities

- **Study** - Clinical trial
- **Site** - Research location
- **Subject** - Trial participant

## Commands

- `DesignStudy` - Create protocol
- `ActivateSite` - Enable location
- `EnrollSubject` - Add participant
- `RecordVisit` - Document encounter
- `SubmitData` - Upload findings

## Events

- `StudyDesigned` - Protocol created
- `SiteActivated` - Location enabled
- `SubjectEnrolled` - Participant added
- `VisitRecorded` - Encounter documented
- `DataSubmitted` - Findings uploaded

## Integration Points

- EDC systems
- CTMS
- Regulatory systems
- Safety databases