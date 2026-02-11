# Assembly Operations

Work instructions, assembly tracking, and production execution.

## NAICS Code

**332000** - Fabricated Metal Product Manufacturing

## Scope

This model covers assembly operations, including:

- Work instruction management
- Station and line configuration
- Assembly sequence tracking
- Component consumption
- Quality checkpoints

## Key Concepts

| Concept | Description |
|---------|-------------|
| WorkInstruction | Step-by-step assembly guidance |
| Station | A work position on the production line |
| Assembly | A unit being built with tracked progress |
| Component | Parts consumed during assembly |

## Related Patterns

- `patterns/entity/event-sourced/` - For assembly genealogy
- `patterns/workflow/process-manager/` - For line coordination
