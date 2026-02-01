# Portfolio Operations

PE portfolio company management.

## Overview

This model manages portfolio company operations including value creation
initiatives, governance, and exit planning.

## Key Entities

- **PortfolioCompany** - Owned company
- **Initiative** - Value creation project
- **Exit** - Disposition plan

## Commands

- `LaunchInitiative` - Start project
- `TrackProgress` - Update status
- `HoldBoardMeeting` - Record governance
- `PlanExit` - Prepare disposition
- `ExecuteExit` - Complete sale

## Events

- `InitiativeLaunched` - Project started
- `ProgressUpdated` - Status refreshed
- `BoardMeetingHeld` - Meeting recorded
- `ExitPlanned` - Disposition planned
- `ExitCompleted` - Sale completed

## Integration Points

- Fund administration
- Financial reporting
- Board management
- Investment banking