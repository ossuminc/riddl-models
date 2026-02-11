# Portfolio Management

Portfolio company monitoring and support.

## NAICS Code

**523910** - Miscellaneous Intermediation

## Overview

This model tracks portfolio company performance, board participation,
and value-add activities.

## Key Entities

- **PortfolioCompany** - Invested company
- **BoardSeat** - Governance role
- **Milestone** - Company achievement

## Commands

- `AddCompany` - Record investment
- `UpdateMetrics` - Refresh performance
- `RecordMeeting` - Log board meeting
- `TrackMilestone` - Note achievement
- `PlanExit` - Prepare for exit

## Events

- `CompanyAdded` - Investment recorded
- `MetricsUpdated` - Performance refreshed
- `MeetingRecorded` - Board meeting logged
- `MilestoneAchieved` - Goal reached
- `ExitPlanned` - Exit preparation started

## Integration Points

- Deal flow
- Fund administration
- Document management
- Communication tools