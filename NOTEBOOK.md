# NOTEBOOK.md - riddl-models

Development journal for active work on the riddl-models repository.

---

## Current Status

**Date**: 2026-02-02
**Phase**: Model Generation - Major Progress

Progress: **85 of 172 models** completed (49% complete)
- 85 domain models created, validated, and committed
- 87 models remaining across various sectors

**Validation**: Use `riddlc from <config>.conf validate` for all models.
**riddlc location**: `../riddl/riddlc/jvm/target/universal/stage/bin/riddlc`

---

## Completed Work

### 2026-02-02: Continued Model Generation (68 Models)

Continued systematic generation across multiple sectors:

**Government Sector (7 models):**
- `regulatory/licensing` - Professional/business license management
- `public-safety/emergency-dispatch` - 911 emergency dispatch
- `public-safety/records-management` - Law enforcement records
- `citizen-services/case-management` - Citizen service requests
- `citizen-services/benefits-administration` - Benefits programs
- `citizen-services/permit-management` - Building permits

**Professional Services (1 model):**
- `accounting/client-accounting` - Accounting engagement management

**Technology Sector (4 models):**
- `saas/usage-metering` - SaaS usage tracking and billing
- `saas/subscription-management` - Subscription lifecycle
- `saas/tenant-provisioning` - Multi-tenant provisioning
- `devops/ci-cd-pipeline` - CI/CD pipeline orchestration
- `devops/infrastructure-as-code` - IaC deployment
- `devops/observability` - Monitoring and alerting

**Finance Sector (9 models):**
- `banking/account-management` - Bank account operations
- `banking/loan-origination` - Loan application processing
- `banking/credit-decisioning` - Credit risk evaluation
- `payments/payment-processing` - Payment transactions
- `payments/merchant-acquiring` - Merchant onboarding
- `payments/digital-wallet` - Digital wallet operations
- `payments/fund-transfer` - Money transfers
- `trading/order-management` - Trading order execution
- `trading/trade-settlement` - Trade settlement

**Healthcare Sector (5 models):**
- `hospitals/patient-registration` - Patient intake
- `hospitals/appointment-scheduling` - Appointment management
- `clinical/clinical-encounter` - Clinical documentation
- `clinical/care-coordination` - Care team coordination
- `payer/claims-adjudication` - Claims processing

**Insurance Sector (2 models):**
- `property-casualty/policy-management` - P&C policy lifecycle
- `property-casualty/claims-adjudication` - Claims processing

**Manufacturing Sector (2 models):**
- `maintenance/work-order-management` - Work order processing
- `discrete/inventory-management` - Inventory tracking

**Transportation Sector (11 models):**
- `passenger/ride-sharing` - Ride-sharing operations
- `passenger/airline-reservations` - Flight bookings
- `passenger/transit-operations` - Public transit
- `freight/freight-forwarding` - Freight logistics
- `freight/intermodal` - Intermodal transport
- `freight/customs-brokerage` - Customs clearance
- `fleet/fleet-management` - Fleet operations
- `fleet/route-optimization` - Route planning
- `maritime/port-operations` - Port logistics
- `maritime/vessel-management` - Vessel tracking

**Hospitality Sector (8 models):**
- `lodging/hotel-reservations` - Hotel bookings
- `lodging/guest-services` - Guest management
- `lodging/property-management` - Property operations
- `food-service/restaurant-operations` - Restaurant management
- `food-service/catering-management` - Catering services
- `travel/tour-operations` - Tour packages
- `travel/car-rental` - Vehicle rentals
- `events/venue-management` - Venue operations
- `events/event-registration` - Event ticketing

**Entertainment Sector (5 models):**
- `media/content-management` - Media content
- `media/streaming-platform` - Streaming services
- `gaming/matchmaking` - Game matchmaking
- `gaming/game-economy` - Virtual economies
- `marketing/advertising-delivery` - Ad serving

**Education Sector (6 models):**
- `academic/course-management` - Course catalog
- `academic/learning-management` - LMS
- `academic/student-information` - Student records
- `certification/credentialing` - Certification tracking
- `corporate-training/competency-management` - Skills tracking
- `corporate-training/training-administration` - Training programs

**Engineering Sector (6 models):**
- `consulting/engagement-management` - Consulting engagements
- `consulting/knowledge-management` - Knowledge base
- `product-development/plm-integration` - PLM systems
- `product-development/prototype-management` - Prototyping
- `product-development/design-review` - Design reviews
- `project-engineering/engineering-project` - Engineering projects

**Investment Sector (1 model):**
- `venture-capital/deal-flow` - Deal pipeline management

### 2026-02-01: Commerce & Construction Sectors (17 Models)

Completed all models for the first two sectors:

**Commerce Sector (10 models):**
- `e-commerce/order-management` - Order lifecycle with fulfillment saga
- `e-commerce/product-catalog` - Product catalog with categories
- `e-commerce/shopping-cart` - Cart management and checkout
- `marketplace/vendor-management` - Vendor onboarding
- `marketplace/order-orchestration` - Multi-vendor orders
- `retail/inventory-management` - Stock tracking
- `retail/point-of-sale` - POS transactions
- `retail/store-operations` - Store management
- `wholesale/distribution` - Wholesale distribution
- `wholesale/trade-credit` - Credit management

**Construction Sector (7 models):**
- `field-operations/equipment-tracking` - Equipment lifecycle
- `field-operations/job-site-management` - Site operations
- `project-management/bid-management` - Bid processing
- `project-management/construction-project` - Project tracking
- `project-management/subcontractor-management` - Subcontractor relations
- `real-estate/property-management` - Property leasing
- `real-estate/transaction-management` - Real estate transactions

---

## Active Work

### Pending: Fix Author Emails

Some early models may have incorrect author email `support@ossum.ai` instead
of the correct `support@ossuminc.com`. Need to audit and fix.

### Pending: Generate Remaining Domain Models

87 models remaining. Continue systematic generation:

| Sector | Status |
|--------|--------|
| commerce | COMPLETE (10) |
| construction | COMPLETE (7) |
| education | COMPLETE (6) |
| engineering | COMPLETE (6) |
| entertainment | PARTIAL (5 of 10) |
| finance | COMPLETE (9) |
| government | COMPLETE (7) |
| healthcare | PARTIAL (5 of 16) |
| hospitality | PARTIAL (8 of 12) |
| insurance | PARTIAL (2 of 4) |
| investment | PARTIAL (1 of 6) |
| logistics | pending (8) |
| manufacturing | PARTIAL (2 of 14) |
| marketing | PARTIAL (1 of 6) |
| natural-resources | pending (8) |
| professional-services | PARTIAL (1 of 6) |
| technology | PARTIAL (6 of 9) |
| telecommunications | pending (6) |
| transportation | COMPLETE (11) |
| utilities | pending (8) |

---

## Design Decisions

### Model File Structure (2026-02-01)

Each model uses 6 files:
- `model.conf` - riddlc configuration pointing to main file
- `model.riddl` - Domain definition with includes
- `types.riddl` - Shared type definitions
- `Entity.riddl` - One file per entity
- `Context.riddl` - Main bounded context with repository/projector
- `external-contexts.riddl` - External systems with `option is external`

### RIDDL Syntax Notes (2026-02-01)

Important syntax findings during model generation:
- Enum values cannot have individual `with { briefly ... }` blocks
- Handler `on` clauses work with or without `is` in v1.2.1+
- Identifier minimum length is 3 characters (e.g., `VA` -> `VALoan`)
- User/enum name collisions trigger warnings (use distinct names)
- Collection syntax: `many optional Type` (not `optional many`)
- External contexts: `option is external` in `with` block
- State transitions: `morph entity X to state Y with command Z`
- Entity messaging: `tell event X to entity Y`

### Author Block Pattern (2026-02-02)

Standard author block for all models:
```riddl
author OssumInc is {
  name is "Ossum Inc."
  email is "support@ossuminc.com"
}
```

---

## Blockers

- **None currently**

---

## Notes

- riddlc path: `../riddl/riddlc/jvm/target/universal/stage/bin/riddlc`
- Version 1.2.1+ required for validation
- All models validated with only `???` placeholder warnings (no errors)
