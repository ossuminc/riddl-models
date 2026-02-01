# Clinical

Outpatient clinical care delivery and patient management.

## Scope

This subsector covers ambulatory care settings and clinical workflows,
including:

- Patient registration and demographics
- Appointment scheduling and check-in
- Clinical encounter documentation
- Care coordination and referrals
- Clinical decision support

## Models

| Model | Description |
|-------|-------------|
| `patient-registration/` | Demographics, insurance, and consent |
| `appointment-scheduling/` | Provider availability and booking |
| `clinical-encounter/` | Visit documentation and orders |
| `care-coordination/` | Referrals and care team communication |

## Related Patterns

- `patterns/entity/aggregate-root/` - For patient records
- `patterns/workflow/process-manager/` - For care pathways