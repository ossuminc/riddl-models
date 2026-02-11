# Operating Room

Surgery scheduling and management.

## NAICS Code

**622110** - General Medical and Surgical Hospitals

## Overview

This model manages operating room scheduling, case management, and
surgical workflow.

## Key Entities

- **Case** - Surgical procedure
- **Room** - Operating room
- **Team** - Surgical staff

## Commands

- `ScheduleCase` - Book surgery
- `PrepareRoom` - Ready OR
- `StartCase` - Begin surgery
- `CompleteCase` - End surgery
- `TurnoverRoom` - Prepare for next

## Events

- `CaseScheduled` - Surgery booked
- `RoomPrepared` - OR ready
- `CaseStarted` - Surgery began
- `CaseCompleted` - Surgery ended
- `RoomTurnedOver` - Ready for next

## Integration Points

- Scheduling systems
- Preference cards
- Supply chain
- Anesthesia records