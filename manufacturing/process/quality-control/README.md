# Quality Control

Inspections, specifications, and quality holds.

## Scope

This model covers quality control operations, including:

- Inspection plan management
- Sample collection and testing
- Specification compliance checking
- Quality holds and releases
- Non-conformance reporting (NCR)

## Key Concepts

| Concept | Description |
|---------|-------------|
| InspectionPlan | Required tests and acceptance criteria |
| Sample | Material collected for testing |
| Result | Test outcome with pass/fail status |
| Hold | A quality block on material |

## Related Patterns

- `patterns/entity/event-sourced/` - For quality history
- `patterns/workflow/process-manager/` - For NCR disposition
