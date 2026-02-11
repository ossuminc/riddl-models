# Loan Origination

Loan application and underwriting.

## NAICS Code

**522110** - Commercial Banking

## Overview

This model handles loan applications from submission through approval,
including document collection, underwriting, and closing.

## Key Entities

- **Application** - Loan application
- **Underwriting** - Risk assessment
- **Closing** - Loan funding

## Commands

- `SubmitApplication` - Start application
- `RequestDocuments` - Gather requirements
- `UnderwriteLoan` - Assess risk
- `ApproveConditionally` - Conditional approval
- `CloseLoan` - Fund the loan

## Events

- `ApplicationSubmitted` - Application started
- `DocumentsReceived` - Requirements gathered
- `UnderwritingComplete` - Decision made
- `LoanApproved` - Application approved
- `LoanFunded` - Disbursement complete

## Integration Points

- Credit bureaus
- Income verification
- Document management
- Servicing systems