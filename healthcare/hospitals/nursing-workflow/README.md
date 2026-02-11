# Nursing Workflow Domain Model

## NAICS Code

**622110** - General Medical and Surgical Hospitals

## Overview

The Nursing Workflow domain models hospital nursing operations including shift
management, patient assignments, task tracking, clinical documentation, and
care handoffs. It follows reactive DDD patterns with event sourcing for the
core NurseShift aggregate.

## Domain Structure

```
nursing-workflow/
├── nursing-workflow.conf     # riddlc configuration
├── nursing-workflow.riddl    # Domain entry point
├── types.riddl               # Shared types and records
├── NurseShift.riddl          # Core entity aggregate
├── NursingContext.riddl      # Bounded context with repository/projectors
├── external-contexts.riddl   # External system integrations
└── README.md                 # This file
```

## Key Concepts

### Users

- **ChargeNurse**: Manages unit operations, staffing, and patient assignments
- **StaffNurse**: Provides direct patient care and documentation
- **NurseAide**: Assists with delegated patient care tasks
- **NurseManager**: Oversees unit performance and quality metrics

### Core Entity: NurseShift

The NurseShift entity is the primary aggregate managing:

- **Shift lifecycle**: Start, active, handoff, completed states
- **Patient assignments**: Acuity-based workload distribution
- **Task management**: Creation, prioritization, completion tracking
- **Clinical documentation**: Assessments and vital signs
- **SBAR handoffs**: Structured communication for care continuity

### States

1. **ActiveState**: Shift is in progress, all activities allowed
2. **HandoffState**: Shift is transitioning, documentation continues
3. **CompletedState**: Shift has ended, summary available

### Commands

- `StartShift` - Begin a nursing shift
- `AssignPatients` - Assign patients to nurse
- `CreateTask` - Add task to worklist
- `CompleteTask` - Mark task as done
- `DocumentAssessment` - Record patient assessment
- `RecordVitals` - Document vital signs
- `InitiateHandoff` - Begin SBAR handoff
- `CompleteHandoff` - Finalize handoff

### Events

- `ShiftStarted` - Shift has begun
- `PatientsAssigned` - Patients assigned to nurse
- `TaskCreated` - New task added
- `TaskCompleted` - Task finished
- `AssessmentDocumented` - Assessment recorded
- `VitalsRecorded` - Vital signs documented
- `HandoffInitiated` - Handoff started
- `HandoffCompleted` - Handoff acknowledged

### External Integrations

- **ADTService**: Patient census, admissions, discharges, transfers
- **OrderManagement**: Clinical orders requiring nursing action
- **MedicationAdministration**: eMAR integration for medication tracking

## Validation

```bash
riddlc from nursing-workflow.conf validate
```

## Use Cases

The epic covers these primary workflows:

1. **Start Shift**: Nurse reviews census and begins shift
2. **Patient Assignment**: Charge nurse distributes patients by acuity
3. **Task Management**: Complete and document nursing tasks
4. **Assessment Documentation**: Record patient assessments
5. **Vital Signs**: Record and validate vital sign measurements
6. **Shift Handoff**: SBAR communication to incoming nurse

## Related Models

- `operating-room/` - Surgical workflow integration
- `care-coordination/` - Multi-disciplinary care planning
- `patient-registration/` - Patient demographics and admission
