# Utilities & Energy

RIDDL models for electric, gas, water utilities, and smart metering.

## Subsectors

### electric/
Electric utility operations.

**Models:**
- `grid-operations/` - Generation, transmission, distribution
- `outage-management/` - Detection, dispatch, restoration

### gas/
Natural gas distribution.

**Models:**
- `gas-distribution/` - Metering, pressure, safety

### water/
Water and wastewater utilities.

**Models:**
- `water-utility/` - Treatment, distribution, billing

### metering/
Smart metering and billing.

**Models:**
- `smart-metering/` - AMI, usage collection, analytics
- `billing-settlement/` - Rate application, invoicing

## Common Patterns

Utilities models frequently use:
- Event sourcing for meter reading history
- Real-time projectors for grid monitoring
- Saga patterns for service orders
- Integration adapters for SCADA and AMI

## Domain-Specific Concepts

- **AMI** - Advanced Metering Infrastructure
- **SCADA** - Supervisory Control and Data Acquisition
- **OMS** - Outage Management System
- **DER** - Distributed Energy Resources