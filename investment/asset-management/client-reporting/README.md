# Client Reporting

Investment statements and communications.

## NAICS Code

**523920** - Portfolio Management and Investment Advice

## Overview

This model generates client reports including statements, performance
summaries, and regulatory disclosures.

## Key Entities

- **Report** - Client document
- **Statement** - Account summary
- **Disclosure** - Regulatory document

## Commands

- `GenerateStatement` - Create account summary
- `CalculateReturns` - Compute performance
- `PrepareDisclosure` - Create regulatory doc
- `DeliverReport` - Send to client
- `ArchiveReport` - Store for retention

## Events

- `StatementGenerated` - Summary created
- `ReturnsCalculated` - Performance computed
- `DisclosurePrepared` - Document ready
- `ReportDelivered` - Sent to client
- `ReportArchived` - Stored

## Integration Points

- Portfolio management
- Performance analytics
- Document delivery
- Compliance systems