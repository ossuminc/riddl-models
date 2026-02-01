# Radiology Workflow

Imaging orders and interpretation.

## Overview

This model manages radiology workflow including order scheduling, image
acquisition, interpretation, and reporting.

## Key Entities

- **Exam** - Imaging study
- **Image** - Acquired images
- **Report** - Radiologist findings

## Commands

- `ScheduleExam` - Book imaging
- `AcquireImages` - Perform study
- `InterpretStudy` - Radiologist review
- `SignReport` - Finalize findings
- `CommunicateCritical` - Alert critical

## Events

- `ExamScheduled` - Imaging booked
- `ImagesAcquired` - Study performed
- `StudyInterpreted` - Review complete
- `ReportSigned` - Findings finalized
- `CriticalCommunicated` - Alert sent

## Integration Points

- PACS systems
- Order entry
- Speech recognition
- EHR systems