# Manufacturing & Production

RIDDL models for discrete manufacturing, process industries, and maintenance.

## Subsectors

### discrete/
Discrete manufacturing (individual units).

**Models:**
- `work-order-management/` - Scheduling, execution, completion
- `bill-of-materials/` - BOM structure, versioning, costing
- `assembly-operations/` - Work instructions, tracking

### process/
Process manufacturing (continuous/batch).

**Models:**
- `batch-processing/` - Recipes, batches, genealogy
- `quality-control/` - Inspections, specs, holds

### machining/
Precision machining and CNC operations.

**Models:**
- `cnc-operations/` - Programs, tooling, cycles
- `precision-manufacturing/` - Tolerances, metrology, certification

### textiles/
Textile and apparel manufacturing.

**Models:**
- `fabric-production/` - Weaving, dyeing, finishing
- `apparel-manufacturing/` - Cut, sew, trim, packaging

### maintenance/
Equipment maintenance and asset management.

**Models:**
- `equipment-maintenance/` - PM, CM, condition-based
- `asset-lifecycle/` - Acquisition, depreciation, disposal

## Common Patterns

Manufacturing models frequently use:
- Multi-state entities for work order lifecycle
- Event sourcing for production genealogy/traceability
- Saga patterns for production scheduling
- Projectors for production dashboards

## Domain-Specific Concepts

- **BOM** - Bill of Materials
- **WIP** - Work in Process
- **PM/CM** - Preventive/Corrective Maintenance
- **OEE** - Overall Equipment Effectiveness