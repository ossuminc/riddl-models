# Education & Training

RIDDL models for academic institutions, corporate training, and certification.

## Subsectors

### academic/
K-12 and higher education operations.

**Models:**
- `student-information/` - Enrollment, records, transcripts
- `course-management/` - Catalog, scheduling, registration
- `learning-management/` - Content, assignments, grades

### corporate-training/
Enterprise training and development.

**Models:**
- `training-administration/` - Programs, enrollment, completion
- `competency-management/` - Skills, assessments, gaps

### certification/
Professional certification and credentialing.

**Models:**
- `credentialing/` - Exams, certificates, renewals

## Common Patterns

Education models frequently use:
- Multi-state entities for enrollment lifecycle
- Event sourcing for academic records
- Projectors for grade books and dashboards
- Integration adapters for LMS platforms

## Compliance Considerations

Education models must address:
- FERPA (student privacy)
- Accreditation requirements
- Transcript integrity
- Accessibility (ADA/WCAG)

## Domain-Specific Concepts

- **LMS** - Learning Management System
- **SIS** - Student Information System
- **FERPA** - Family Educational Rights and Privacy Act