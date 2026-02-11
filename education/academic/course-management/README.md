# Course Management

Course catalog, scheduling, and registration.

## NAICS Code

**611310** - Colleges, Universities, and Professional Schools

## Scope

This model covers course administration, including:

- Course catalog and curriculum
- Section scheduling and capacity
- Student registration and waitlists
- Instructor assignment
- Room and resource allocation

## Key Concepts

| Concept | Description |
|---------|-------------|
| Course | A defined learning unit in the catalog |
| Section | A scheduled offering of a course |
| Registration | A student's enrollment in a section |
| Schedule | The time, location, and instructor for sections |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For registration workflows
- `patterns/projection/read-model/` - For schedule and availability views
