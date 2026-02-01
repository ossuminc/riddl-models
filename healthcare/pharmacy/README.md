# Pharmacy

Medication management and pharmaceutical dispensing.

## Scope

This subsector covers pharmacy operations for both retail and health system
pharmacies, including:

- Prescription processing and verification
- Drug interaction checking
- Medication dispensing and labeling
- Inventory and formulary management
- Patient counseling and MTM

## Models

| Model | Description |
|-------|-------------|
| `prescription-management/` | Rx intake, verification, and refills |
| `medication-dispensing/` | Fill, label, and dispense workflows |

## Related Patterns

- `patterns/workflow/process-manager/` - For dispensing workflows
- `patterns/entity/event-sourced/` - For prescription history