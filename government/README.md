# Government & Public Sector

RIDDL models for citizen services, regulatory compliance, and public safety.

## Subsectors

### citizen-services/
Government services to citizens.

**Models:**
- `permit-management/` - Applications, reviews, issuance
- `case-management/` - Intake, investigation, resolution
- `benefits-administration/` - Eligibility, enrollment, payments

### regulatory/
Regulatory compliance and enforcement.

**Models:**
- `licensing/` - Applications, renewals, enforcement
- `compliance-reporting/` - Filings, audits, penalties

### public-safety/
Emergency services and public safety.

**Models:**
- `emergency-dispatch/` - CAD, units, incidents
- `records-management/` - Evidence, reports, retention

## Common Patterns

Government models frequently use:
- Event sourcing for complete audit trails
- Multi-state entities for case/permit lifecycle
- Saga patterns for approval workflows
- Strong access controls for PII

## Compliance Considerations

Government models must address:
- Records retention requirements
- Freedom of Information Act (FOIA)
- ADA accessibility
- Data sovereignty

## Domain-Specific Concepts

- **CAD** - Computer-Aided Dispatch
- **FOIA** - Freedom of Information Act
- **PII** - Personally Identifiable Information