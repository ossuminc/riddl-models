# Bill of Materials

BOM structure, versioning, and cost rollup.

## Scope

This model covers BOM management, including:

- Multi-level BOM structure
- Engineering change management
- Version and effectivity control
- Cost rollup and analysis
- Where-used queries

## Key Concepts

| Concept | Description |
|---------|-------------|
| BOM | Hierarchical list of components for a product |
| Component | A part or subassembly in the BOM |
| Revision | A version of the BOM with effectivity dates |
| CostRollup | Calculated total cost from components |

## Related Patterns

- `patterns/entity/aggregate-root/` - For BOM with components
- `patterns/entity/event-sourced/` - For revision history
