# Customs Brokerage

Import/export classification, compliance, and clearance.

## NAICS Code

**488510** - Freight Transportation Arrangement

## Scope

This model covers customs brokerage operations, including:

- Tariff classification (HS codes)
- Import/export documentation
- Duty calculation and payment
- Compliance screening and holds
- Government agency coordination

## Key Concepts

| Concept | Description |
|---------|-------------|
| Entry | A customs declaration for imported goods |
| Classification | HS code assignment determining duty rates |
| Clearance | The release of goods by customs authorities |
| Compliance | Adherence to trade regulations and restrictions |

## Related Patterns

- `patterns/saga/distributed-transaction/` - For multi-agency clearance
- `patterns/workflow/process-manager/` - For entry processing
