# Appointment Scheduling

Provider scheduling and booking.

## Overview

This model manages appointment scheduling including provider availability,
booking, reminders, and check-in.

## Key Entities

- **Appointment** - Scheduled visit
- **Schedule** - Provider availability
- **Reminder** - Patient notification

## Commands

- `BookAppointment` - Schedule visit
- `RescheduleAppointment` - Change time
- `CancelAppointment` - Cancel visit
- `CheckInPatient` - Arrival process
- `SendReminder` - Notify patient

## Events

- `AppointmentBooked` - Visit scheduled
- `AppointmentRescheduled` - Time changed
- `AppointmentCancelled` - Visit cancelled
- `PatientCheckedIn` - Patient arrived
- `ReminderSent` - Notification sent

## Integration Points

- Patient registration
- Provider schedules
- Notification services
- Waitlist management