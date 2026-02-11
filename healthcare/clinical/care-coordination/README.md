# Care Coordination

Referrals and care team communication.

## NAICS Code

**621111** - Offices of Physicians

## Overview

This model manages care coordination including referrals, care plans,
and multi-provider communication.

## Key Entities

- **Referral** - Provider-to-provider request
- **CarePlan** - Treatment goals and tasks
- **CareTeam** - Involved providers

## Commands

- `CreateReferral` - Request consultation
- `AcceptReferral` - Acknowledge request
- `CreateCarePlan` - Define treatment plan
- `UpdateCarePlan` - Modify plan
- `CommunicateStatus` - Share updates

## Events

- `ReferralCreated` - Consultation requested
- `ReferralAccepted` - Request acknowledged
- `CarePlanCreated` - Plan defined
- `CarePlanUpdated` - Plan modified
- `StatusCommunicated` - Update shared

## Integration Points

- Provider directories
- Scheduling
- EHR systems
- Notification services