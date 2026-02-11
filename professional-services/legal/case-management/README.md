# Case Management

Legal case lifecycle management for law firms and legal departments.

## NAICS Code

**541110** - Offices of Lawyers

## Scope

This model covers legal case management, including:

- Case intake and conflict checking
- Attorney and paralegal team assignment
- Time entry and expense tracking
- Document management and case files
- Court calendar and deadline management
- Case status progression and resolution
- Billing and invoicing workflows

## Key Concepts

| Concept | Description |
|---------|-------------|
| LegalCase | A legal matter with full lifecycle tracking |
| TeamMember | Attorney or paralegal assigned to a case |
| TimeEntry | Billable time recorded against a case |
| CaseDocument | Document attached to the case file |
| CourtDate | Scheduled court appearance or deadline |

## Related Patterns

- `patterns/entity/event-sourced/` - For case history
- `patterns/entity/aggregate-root/` - For case with team and documents
