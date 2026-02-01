# Design Review

Submittal management, approvals, and revision tracking.

## Scope

This model covers design review operations, including:

- Submittal creation and submission
- Review assignment and routing
- Comment collection and resolution
- Approval and revision control
- Design milestone sign-off

## Key Concepts

| Concept | Description |
|---------|-------------|
| Submittal | A design document for review |
| Review | An evaluation with comments |
| Revision | An updated version of a design |
| Approval | Sign-off on a design stage |

## Related Patterns

- `patterns/entity/event-sourced/` - For revision history
- `patterns/workflow/process-manager/` - For review routing
