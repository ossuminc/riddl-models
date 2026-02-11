# Design Review

Engineering design review, approval, and change management.

## NAICS Code

**541330** - Engineering Services

## Scope

This model covers design review processes, including:

- Design submission and review scheduling
- Reviewer assignment and comment tracking
- Decision recording with outcomes and conditions
- Revision request and resubmission workflows
- Review finalization and cancellation

## Key Concepts

| Concept | Description |
|---------|-------------|
| Review | A formal evaluation of an engineering design |
| ReviewerAssignment | An engineer assigned to evaluate a design |
| ReviewComment | Feedback from a reviewer with priority and status |
| ReviewDecision | A reviewer's outcome (approved, needs revision, etc.) |
| ActionItem | A task arising from review findings |
| DesignDocument | Supporting documentation under review |

## Related Patterns

- `patterns/entity/event-sourced/` - For review history tracking
- `patterns/workflow/process-manager/` - For approval workflows
