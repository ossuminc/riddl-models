# Member Enrollment

Health plan enrollment and eligibility.

## Overview

This model manages member enrollment including plan selection, eligibility
determination, and coverage maintenance.

## Key Entities

- **Member** - Enrolled individual
- **Enrollment** - Coverage period
- **Eligibility** - Benefit access

## Commands

- `EnrollMember` - Add to plan
- `SelectPlan` - Choose coverage
- `TerminateCoverage` - End enrollment
- `TransferEnrollment` - Change plans
- `VerifyEligibility` - Check coverage

## Events

- `MemberEnrolled` - Added to plan
- `PlanSelected` - Coverage chosen
- `CoverageTerminated` - Enrollment ended
- `EnrollmentTransferred` - Plan changed
- `EligibilityVerified` - Coverage confirmed

## Integration Points

- Exchanges/marketplaces
- Employer groups
- Benefits administration
- Claims systems