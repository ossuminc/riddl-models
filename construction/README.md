# Construction & Real Estate

RIDDL models for construction project management, field operations, and real
estate.

## Subsectors

### project-management/
Construction project planning and control.

**Models:**
- `construction-project/` - Planning, scheduling, cost control
- `bid-management/` - RFPs, estimates, awards
- `subcontractor-management/` - Contracts, compliance, payments

### field-operations/
Job site management and field work.

**Models:**
- `job-site-management/` - Daily logs, inspections, safety
- `equipment-tracking/` - Fleet, utilization, maintenance

### real-estate/
Property management and transactions.

**Models:**
- `property-management/` - Leases, tenants, maintenance
- `transaction-management/` - Listings, offers, closings

## Common Patterns

Construction models frequently use:
- Multi-state entities for project phases
- Saga patterns for procurement workflows
- Projectors for project status dashboards
- Integration adapters for CAD/BIM systems

## Domain-Specific Concepts

- **RFP/RFQ** - Request for Proposal/Quote
- **Change Order** - Approved project modification
- **Punch List** - Pre-completion defect list
- **Retainage** - Withheld payment until completion