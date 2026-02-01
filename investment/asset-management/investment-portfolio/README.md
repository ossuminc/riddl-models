# Investment Portfolio

Holdings and portfolio management.

## Overview

This model manages investment portfolios including holdings, allocations,
rebalancing, and performance tracking.

## Key Entities

- **Portfolio** - Collection of holdings
- **Holding** - Security position
- **Allocation** - Target weights

## Commands

- `CreatePortfolio` - Open portfolio
- `ExecuteTrade` - Buy or sell
- `Rebalance` - Adjust allocations
- `CalculatePerformance` - Compute returns
- `GenerateReport` - Create statement

## Events

- `PortfolioCreated` - Portfolio opened
- `TradeExecuted` - Position changed
- `PortfolioRebalanced` - Weights adjusted
- `PerformanceCalculated` - Returns computed
- `ReportGenerated` - Statement created

## Integration Points

- Trading systems
- Market data
- Performance analytics
- Client reporting