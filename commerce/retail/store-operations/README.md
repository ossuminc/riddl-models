# Store Operations

Daily store management and staffing.

## NAICS Code

**452000** - General Merchandise Retailers

## Overview

This model handles store operational activities including opening/closing,
staff scheduling, daily reporting, and task management.

## Key Entities

- **Store** - Physical location and configuration
- **Shift** - Staff work period
- **DailyReport** - End-of-day summary

## Commands

- `OpenStore` - Begin business day
- `CloseStore` - End business day
- `ScheduleShift` - Assign staff schedule
- `ClockIn` - Record arrival
- `SubmitReport` - Complete daily summary

## Events

- `StoreOpened` - Business day started
- `StoreClosed` - Business day ended
- `ShiftScheduled` - Staff assigned
- `EmployeeClocked` - Time recorded
- `ReportSubmitted` - Daily summary complete

## Integration Points

- HR for employee data
- Payroll for time tracking
- Loss prevention
- Corporate reporting