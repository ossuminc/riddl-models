# Investment & Venture Capital

RIDDL models for investment firms, venture capital, private equity, and asset
management operations.

## Subsectors

### venture-capital/
Venture capital fund operations from deal sourcing to portfolio management.

**Models:**
- `deal-flow/` - Sourcing, screening, due diligence
- `portfolio-management/` - Tracking, reporting, follow-on investments
- `fund-administration/` - Capital calls, distributions, LP reporting

### private-equity/
Private equity portfolio operations and value creation.

**Models:**
- `portfolio-operations/` - Value creation plans, exits, monitoring

### asset-management/
Traditional asset management for investment portfolios.

**Models:**
- `investment-portfolio/` - Holdings, rebalancing, performance tracking
- `client-reporting/` - Statements, compliance, disclosures

## Common Patterns

Investment models frequently use:
- Event sourcing for complete audit trails (regulatory compliance)
- Saga patterns for capital call workflows
- Projectors for portfolio performance dashboards