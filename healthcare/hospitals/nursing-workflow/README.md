# Nursing Workflow

Shift management and nursing tasks.

## Overview

This model manages nursing workflows including shift handoffs, task
management, and patient assessments.

## Key Entities

- **Assignment** - Nurse-patient pairing
- **Task** - Care activity
- **Assessment** - Patient evaluation

## Commands

- `AssignPatients` - Create assignments
- `HandoffShift` - Transfer care
- `CompleteTask` - Finish activity
- `DocumentAssessment` - Record evaluation
- `EscalateConcern` - Alert provider

## Events

- `PatientsAssigned` - Assignments made
- `ShiftHandedOff` - Care transferred
- `TaskCompleted` - Activity finished
- `AssessmentDocumented` - Evaluation recorded
- `ConcernEscalated` - Provider alerted

## Integration Points

- ADT systems
- Order management
- Medication administration
- Documentation systems