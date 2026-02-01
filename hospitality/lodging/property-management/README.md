# Property Management

Room status and housekeeping.

## Overview

This model manages hotel property operations including room status,
housekeeping assignments, and maintenance.

## Key Entities

- **Room** - Physical accommodation
- **Assignment** - Housekeeping task
- **WorkOrder** - Maintenance request

## Commands

- `UpdateRoomStatus` - Change room state
- `AssignHousekeeping` - Create task
- `CompleteClean` - Mark room ready
- `CreateWorkOrder` - Request repair
- `CompleteWorkOrder` - Finish repair

## Events

- `RoomStatusUpdated` - State changed
- `HousekeepingAssigned` - Task created
- `CleanCompleted` - Room ready
- `WorkOrderCreated` - Repair requested
- `WorkOrderCompleted` - Repair finished

## Integration Points

- Reservations
- Guest services
- Engineering
- Inventory management