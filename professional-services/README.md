# Professional Services

RIDDL models for legal, accounting, and HR services.

## Subsectors

### legal/
Law firm and legal operations.

**Models:**
- `matter-management/` - Cases, tasks, deadlines
- `contract-lifecycle/` - Drafting, negotiation, execution

### accounting/
Accounting and audit services.

**Models:**
- `client-accounting/` - Engagements, workpapers, delivery
- `audit-management/` - Planning, testing, reporting

### hr-services/
Human resources and staffing.

**Models:**
- `recruiting/` - Requisitions, candidates, hiring
- `payroll-processing/` - Time, pay, taxes, disbursement
- `benefits-administration/` - Enrollment, claims, compliance

## Common Patterns

Professional services models frequently use:
- Multi-state entities for matter/engagement lifecycle
- Event sourcing for complete work history
- Saga patterns for approval workflows
- Time tracking for billable hours

## Compliance Considerations

Professional services must address:
- Client confidentiality
- Regulatory compliance (SOX, etc.)
- Conflict of interest checks
- Professional licensing requirements

## Domain-Specific Concepts

- **SOW** - Statement of Work
- **WIP** - Work in Progress
- **Realization** - Billed vs. worked hours ratio