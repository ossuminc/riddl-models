# Portfolio Management

PE portfolio company investment and value creation management.

## NAICS Code

**523910** - Miscellaneous Intermediation

## Overview

This model manages private equity portfolio company investments
from acquisition through exit, including financial monitoring,
valuation tracking, follow-on investments, board governance, and
investment write-offs.

## Key Entities

- **PortfolioCompany** - Owned company with investment details
- **ValuationInfo** - Company valuation with method and multiples
- **FinancialMetrics** - Revenue, EBITDA, and other KPIs
- **BoardMember** - Fund representative on company board

## Commands

- `AcquireCompany` - Add company to portfolio
- `UpdateCompanyInfo` - Update company details
- `RecordFinancials` - Record financial performance
- `UpdateValuation` - Record new valuation
- `MakeFollowOn` - Make follow-on investment
- `AppointBoardMember` - Appoint board representative
- `RemoveBoardMember` - Remove board representative
- `ExitInvestment` - Record investment exit
- `WriteOffInvestment` - Write off investment

## Events

- `CompanyAcquired` - Added to portfolio
- `CompanyInfoUpdated` - Details updated
- `FinancialsRecorded` - Financials recorded
- `ValuationUpdated` - Valuation changed
- `FollowOnMade` - Additional investment made
- `BoardMemberAppointed` - Board seat filled
- `BoardMemberRemoved` - Board seat vacated
- `InvestmentExited` - Exit completed
- `InvestmentWrittenOff` - Investment written off

## Integration Points

- Fund administration
- Market data and valuation services
- Legal document management
- Investor relations
