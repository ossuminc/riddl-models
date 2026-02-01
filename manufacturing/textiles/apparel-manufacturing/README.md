# Apparel Manufacturing

Cut, sew, trim operations for garment production.

## Scope

This model covers apparel manufacturing, including:

- Marker making and cutting
- Sewing line management
- Bundle and piece tracking
- Trim and finishing
- Packing and labeling

## Key Concepts

| Concept | Description |
|---------|-------------|
| CutOrder | A cutting job with markers and layers |
| Bundle | A group of cut pieces for sewing |
| SewingOperation | A garment assembly step |
| Garment | A finished apparel item |

## Related Patterns

- `patterns/workflow/process-manager/` - For production flow
- `patterns/entity/event-sourced/` - For piece tracking
