# Healthcare & Life Sciences

RIDDL models for hospitals, clinical care, pharmacy, payers, and life sciences.

## Subsectors

### hospitals/
Hospital operations and clinical workflows.

**Models:**
- `admission-discharge/` - ADT, bed management, transfers
- `operating-room/` - Scheduling, staffing, turnover
- `nursing-workflow/` - Assignments, rounds, documentation
- `lab-orders/` - Order entry, specimen, results
- `radiology-workflow/` - Orders, scheduling, PACS integration
- `supply-chain/` - Par levels, requisitions, expiry

### clinical/
Ambulatory and clinical care operations.

**Models:**
- `patient-registration/` - Demographics, insurance, consent
- `appointment-scheduling/` - Booking, reminders, check-in
- `clinical-encounter/` - Visit, diagnosis, orders
- `care-coordination/` - Referrals, transitions, follow-up

### pharmacy/
Prescription and medication management.

**Models:**
- `prescription-management/` - e-Prescribe, renewals, transfers
- `medication-dispensing/` - Fill, verify, counsel, dispense

### payer/
Health insurance and claims operations.

**Models:**
- `claims-adjudication/` - Submission, processing, payment
- `member-enrollment/` - Eligibility, plans, benefits

### life-sciences/
Pharmaceutical and clinical research.

**Models:**
- `clinical-trials/` - Protocol, enrollment, data collection
- `drug-supply-chain/` - Track-and-trace, serialization

## Common Patterns

Healthcare models frequently use:
- Event sourcing for complete medical record history
- Multi-state entities for patient encounters
- Saga patterns for order workflows
- Strong access control for PHI

## Compliance Considerations

Healthcare models must address:
- HIPAA privacy and security
- Audit trails for all data access
- Consent management
- Data retention policies