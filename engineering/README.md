# Engineering Services

RIDDL models for engineering projects, product development, and consulting.

## Subsectors

### project-engineering/
Engineering project management.

**Models:**
- `engineering-project/` - Scope, milestones, deliverables
- `design-review/` - Submittals, approvals, revisions

### product-development/
Product lifecycle management.

**Models:**
- `plm-integration/` - CAD, BOM, change management
- `prototype-management/` - Builds, testing, iteration

### consulting/
Engineering consulting and professional services.

**Models:**
- `engagement-management/` - SOWs, resources, billing
- `knowledge-management/` - Expertise, lessons learned

## Common Patterns

Engineering models frequently use:
- Multi-state entities for design review workflows
- Event sourcing for design version history
- Saga patterns for change request workflows
- Integration adapters for CAD/PLM systems

## Integration Points

Engineering models often integrate with:
- CAD systems (AutoCAD, SolidWorks)
- PLM systems (Windchill, Teamcenter)
- Project management tools
- ERP systems