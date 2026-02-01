# Natural Resources & Mining

RIDDL models for mining, oil & gas, forestry, and agriculture.

## Subsectors

### mining/
Mining and mineral extraction operations.

**Models:**
- `mine-operations/` - Planning, extraction, processing
- `mineral-tracking/` - Grades, stockpiles, shipments

### oil-gas/
Oil and gas exploration and production.

**Models:**
- `well-management/` - Drilling, completion, production
- `pipeline-operations/` - Flow, custody transfer, scheduling

### forestry/
Timber and forest management.

**Models:**
- `harvest-planning/` - Timber inventory, cutting plans
- `log-tracking/` - Scaling, transport, mill delivery

### agriculture/
Farm and livestock management.

**Models:**
- `farm-management/` - Fields, crops, inputs, yields
- `livestock-management/` - Herds, health, movements

## Common Patterns

Natural resources models frequently use:
- Event sourcing for production history
- Multi-state entities for well/mine lifecycle
- Projectors for production dashboards
- Integration adapters for SCADA systems

## Domain-Specific Concepts

- **SCADA** - Supervisory Control and Data Acquisition
- **MBF** - Thousand Board Feet (timber)
- **BOE** - Barrel of Oil Equivalent
- **JORC/NI 43-101** - Mineral reporting standards