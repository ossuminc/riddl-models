# NAICS Code Index

Maps [NAICS](https://www.census.gov/naics/) industry classification
codes to RIDDL models in this repository. Organized by the standard
NAICS sector hierarchy (2-digit sector, 3-digit subsector, then
full industry code).

**187 models** across **20 NAICS sectors**, **61 unique codes**.

---

## 11 - Agriculture, Forestry, Fishing and Hunting

### 111 - Crop Production

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 111000 | Crop Production | Crop Management | `natural-resources/agriculture/crop-management` |
| 111000 | Crop Production | Farm Management | `natural-resources/agriculture/farm-management` |

### 112 - Animal Production and Aquaculture

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 112000 | Animal Production and Aquaculture | Livestock Management | `natural-resources/agriculture/livestock-management` |

### 113 - Forestry and Logging

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 113310 | Logging | Harvest Planning | `natural-resources/forestry/harvest-planning` |
| 113310 | Logging | Log Tracking | `natural-resources/forestry/log-tracking` |
| 113310 | Logging | Timber Management | `natural-resources/forestry/timber-management` |

---

## 21 - Mining, Quarrying, and Oil and Gas Extraction

### 211 - Oil and Gas Extraction

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 211120 | Crude Petroleum Extraction | Well Management | `natural-resources/oil-gas/well-management` |

### 212 - Mining (except Oil and Gas)

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 212000 | Mining (except Oil and Gas) | Mine Operations | `natural-resources/mining/mine-operations` |
| 212000 | Mining (except Oil and Gas) | Mineral Tracking | `natural-resources/mining/mineral-tracking` |

---

## 22 - Utilities

### 221 - Utilities

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 221100 | Electric Power Generation, Transmission and Distribution | Billing & Settlement | `utilities/metering/billing-settlement` |
| 221100 | Electric Power Generation, Transmission and Distribution | Smart Metering | `utilities/metering/smart-metering` |
| 221121 | Electric Bulk Power Transmission and Control | Grid Operations | `utilities/electric/grid-operations` |
| 221122 | Electric Power Distribution | Outage Management | `utilities/electric/outage-management` |
| 221210 | Natural Gas Distribution | Gas Distribution | `utilities/gas/gas-distribution` |
| 221310 | Water Supply and Irrigation Systems | Water Distribution | `utilities/water/water-distribution` |
| 221310 | Water Supply and Irrigation Systems | Water Utility | `utilities/water/water-utility` |

---

## 23 - Construction

### 236 - Construction of Buildings

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 236200 | Nonresidential Building Construction | Bid Management | `construction/project-management/bid-management` |
| 236200 | Nonresidential Building Construction | Construction Project | `construction/project-management/construction-project` |
| 236200 | Nonresidential Building Construction | Subcontractor Management | `construction/project-management/subcontractor-management` |

### 238 - Specialty Trade Contractors

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 238000 | Specialty Trade Contractors | Equipment Tracking | `construction/field-operations/equipment-tracking` |
| 238000 | Specialty Trade Contractors | Job Site Management | `construction/field-operations/job-site-management` |

---

## 31-33 - Manufacturing

### 313 - Textile Mills

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 313000 | Textile Mills | Fabric Production | `manufacturing/textiles/fabric-production` |

### 315 - Apparel Manufacturing

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 315000 | Apparel Manufacturing | Apparel Manufacturing | `manufacturing/textiles/apparel-manufacturing` |

### 325 - Chemical Manufacturing

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 325000 | Chemical Manufacturing | Batch Processing | `manufacturing/process/batch-processing` |
| 325000 | Chemical Manufacturing | Quality Control | `manufacturing/process/quality-control` |
| 325411 | Medicinal and Botanical Manufacturing | Drug Supply Chain | `healthcare/life-sciences/drug-supply-chain` |

### 332 - Fabricated Metal Product Manufacturing

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 332000 | Fabricated Metal Product Manufacturing | Assembly Operations | `manufacturing/discrete/assembly-operations` |
| 332000 | Fabricated Metal Product Manufacturing | Bill of Materials | `manufacturing/discrete/bill-of-materials` |
| 332000 | Fabricated Metal Product Manufacturing | Work Order Management | `manufacturing/discrete/work-order-management` |
| 332710 | Machine Shops | CNC Operations | `manufacturing/machining/cnc-operations` |
| 332710 | Machine Shops | Precision Manufacturing | `manufacturing/machining/precision-manufacturing` |

---

## 42 - Wholesale Trade

### 423 - Merchant Wholesalers, Durable Goods

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 423000 | Merchant Wholesalers, Durable Goods | Distribution | `commerce/wholesale/distribution` |
| 423000 | Merchant Wholesalers, Durable Goods | Trade Credit | `commerce/wholesale/trade-credit` |

---

## 44-45 - Retail Trade

### 446 - Health and Personal Care Retailers

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 446110 | Pharmacies and Drug Retailers | Medication Dispensing | `healthcare/pharmacy/medication-dispensing` |
| 446110 | Pharmacies and Drug Retailers | Prescription Management | `healthcare/pharmacy/prescription-management` |

### 452 - General Merchandise Retailers

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 452000 | General Merchandise Retailers | Inventory Management | `commerce/retail/inventory-management` |
| 452000 | General Merchandise Retailers | Point of Sale | `commerce/retail/point-of-sale` |
| 452000 | General Merchandise Retailers | Store Operations | `commerce/retail/store-operations` |

### 454 - Nonstore Retailers

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 454110 | Electronic Shopping and Mail-Order Houses | Order Management | `commerce/e-commerce/order-management` |
| 454110 | Electronic Shopping and Mail-Order Houses | Product Catalog | `commerce/e-commerce/product-catalog` |
| 454110 | Electronic Shopping and Mail-Order Houses | Shopping Cart | `commerce/e-commerce/shopping-cart` |
| 454110 | Electronic Shopping and Mail-Order Houses | Order Orchestration | `commerce/marketplace/order-orchestration` |
| 454110 | Electronic Shopping and Mail-Order Houses | Vendor Management | `commerce/marketplace/vendor-management` |

---

## 48-49 - Transportation and Warehousing

### 481 - Air Transportation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 481111 | Scheduled Passenger Air Transportation | Airline Reservations | `hospitality/travel/airline-reservations` |

### 483 - Water Transportation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 483000 | Water Transportation | Vessel Management | `transportation/maritime/vessel-management` |

### 484 - Truck Transportation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 484000 | Truck Transportation | Fleet Management | `transportation/fleet/fleet-management` |
| 484000 | Truck Transportation | Route Optimization | `transportation/fleet/route-optimization` |

### 485 - Transit and Ground Passenger Transportation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 485110 | Urban Transit Systems | Transit Operations | `transportation/passenger/transit-operations` |
| 485310 | Taxi and Ridesharing Services | Ride Sharing | `transportation/passenger/ride-sharing` |

### 486 - Pipeline Transportation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 486110 | Pipeline Transportation of Crude Oil | Pipeline Operations | `natural-resources/oil-gas/pipeline-operations` |

### 488 - Support Activities for Transportation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 488310 | Port and Harbor Operations | Port Operations | `transportation/maritime/port-operations` |
| 488510 | Freight Transportation Arrangement | Carrier Management | `logistics/freight/carrier-management` |
| 488510 | Freight Transportation Arrangement | Shipment Tracking | `logistics/freight/shipment-tracking` |
| 488510 | Freight Transportation Arrangement | Customs Brokerage | `transportation/freight/customs-brokerage` |
| 488510 | Freight Transportation Arrangement | Freight Forwarding | `transportation/freight/freight-forwarding` |
| 488510 | Freight Transportation Arrangement | Intermodal Transportation | `transportation/freight/intermodal` |

### 492 - Couriers and Messengers

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 492110 | Couriers and Express Delivery Services | Last Mile Delivery | `logistics/freight/last-mile-delivery` |

### 493 - Warehousing and Storage

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 493110 | General Warehousing and Storage | Order Fulfillment | `logistics/fulfillment/order-fulfillment` |
| 493110 | General Warehousing and Storage | Returns Processing | `logistics/fulfillment/returns-processing` |
| 493110 | General Warehousing and Storage | Order Fulfillment | `logistics/supply-chain/order-fulfillment` |
| 493110 | General Warehousing and Storage | Inventory Control | `logistics/warehousing/inventory-control` |
| 493110 | General Warehousing and Storage | Inventory Management | `logistics/warehousing/inventory-management` |
| 493110 | General Warehousing and Storage | Warehouse Management | `logistics/warehousing/warehouse-management` |

---

## 51 - Information

### 511 - Publishing Industries

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 511210 | Software Publishers | Game Economy | `entertainment/gaming/game-economy` |
| 511210 | Software Publishers | Matchmaking | `entertainment/gaming/matchmaking` |
| 511210 | Software Publishers | API Management | `technology/platform/api-management` |
| 511210 | Software Publishers | Identity Management | `technology/platform/identity-management` |
| 511210 | Software Publishers | Customer Success | `technology/saas/customer-success` |
| 511210 | Software Publishers | Multi-Tenant Management | `technology/saas/multi-tenant` |
| 511210 | Software Publishers | Subscription Management | `technology/saas/subscription-management` |
| 511210 | Software Publishers | Tenant Provisioning | `technology/saas/tenant-provisioning` |
| 511210 | Software Publishers | Usage Metering | `technology/saas/usage-metering` |

### 512 - Motion Picture and Sound Recording Industries

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 512110 | Motion Picture and Video Production | Content Management | `entertainment/media/content-management` |

### 515 - Broadcasting and Content Providers

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 515210 | Cable and Other Subscription Programming | Advertising Delivery | `entertainment/media/advertising-delivery` |
| 515210 | Cable and Other Subscription Programming | Streaming Platform | `entertainment/media/streaming-platform` |

### 517 - Telecommunications

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 517311 | Wired Telecommunications Carriers | Revenue Assurance | `telecommunications/billing/revenue-assurance` |
| 517311 | Wired Telecommunications Carriers | Usage Billing | `telecommunications/billing/usage-billing` |
| 517311 | Wired Telecommunications Carriers | Usage Rating | `telecommunications/billing/usage-rating` |
| 517311 | Wired Telecommunications Carriers | Subscriber Management | `telecommunications/customer/subscriber-management` |
| 517311 | Wired Telecommunications Carriers | Trouble Ticketing | `telecommunications/customer/trouble-ticketing` |
| 517311 | Wired Telecommunications Carriers | Equipment Inventory | `telecommunications/network/equipment-inventory` |
| 517311 | Wired Telecommunications Carriers | Network Monitoring | `telecommunications/network/network-monitoring` |
| 517311 | Wired Telecommunications Carriers | Network Operations | `telecommunications/network/network-operations` |
| 517311 | Wired Telecommunications Carriers | Service Provisioning | `telecommunications/network/service-provisioning` |

---

## 52 - Finance and Insurance

### 522 - Credit Intermediation and Related Activities

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 522110 | Commercial Banking | Account Management | `finance/banking/account-management` |
| 522110 | Commercial Banking | Credit Decisioning | `finance/banking/credit-decisioning` |
| 522110 | Commercial Banking | Fund Transfer | `finance/banking/fund-transfer` |
| 522110 | Commercial Banking | Loan Origination | `finance/banking/loan-origination` |
| 522320 | Financial Transactions Processing | Digital Wallet | `finance/payments/digital-wallet` |
| 522320 | Financial Transactions Processing | Merchant Acquiring | `finance/payments/merchant-acquiring` |
| 522320 | Financial Transactions Processing | Payment Processing | `finance/payments/payment-processing` |

### 523 - Securities, Commodity Contracts, and Other Financial Investments

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 523150 | Investment Banking and Securities Intermediation | Order Management | `finance/trading/order-management` |
| 523150 | Investment Banking and Securities Intermediation | Trade Settlement | `finance/trading/trade-settlement` |
| 523910 | Miscellaneous Intermediation | Portfolio Management | `investment/private-equity/portfolio-management` |
| 523910 | Miscellaneous Intermediation | Portfolio Operations | `investment/private-equity/portfolio-operations` |
| 523910 | Miscellaneous Intermediation | Deal Flow | `investment/venture-capital/deal-flow` |
| 523910 | Miscellaneous Intermediation | Fund Administration | `investment/venture-capital/fund-administration` |
| 523910 | Miscellaneous Intermediation | Fund Management | `investment/venture-capital/fund-management` |
| 523910 | Miscellaneous Intermediation | Portfolio Management | `investment/venture-capital/portfolio-management` |
| 523920 | Portfolio Management and Investment Advice | Client Reporting | `investment/asset-management/client-reporting` |
| 523920 | Portfolio Management and Investment Advice | Fund Accounting | `investment/asset-management/fund-accounting` |
| 523920 | Portfolio Management and Investment Advice | Investment Portfolio | `investment/asset-management/investment-portfolio` |

### 524 - Insurance Carriers and Related Activities

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 524113 | Direct Life Insurance Carriers | Policy Lifecycle | `insurance/life-annuity/policy-lifecycle` |
| 524114 | Direct Health and Medical Insurance Carriers | Claims Adjudication | `healthcare/payer/claims-adjudication` |
| 524114 | Direct Health and Medical Insurance Carriers | Member Enrollment | `healthcare/payer/member-enrollment` |
| 524126 | Direct Property and Casualty Insurance Carriers | Claims Processing | `insurance/property-casualty/claims-processing` |
| 524126 | Direct Property and Casualty Insurance Carriers | Policy Administration | `insurance/property-casualty/policy-administration` |
| 524126 | Direct Property and Casualty Insurance Carriers | Policy Management | `insurance/property-casualty/policy-management` |
| 524130 | Reinsurance Carriers | Treaty Management | `insurance/reinsurance/treaty-management` |
| 524292 | Third Party Administration of Insurance Funds | Benefits Administration | `professional-services/hr-services/benefits-administration` |

---

## 53 - Real Estate and Rental and Leasing

### 531 - Real Estate

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 531210 | Offices of Real Estate Agents and Brokers | Transaction Management | `construction/real-estate/transaction-management` |
| 531311 | Residential Property Managers | Property Management | `construction/real-estate/property-management` |

### 532 - Rental and Leasing Services

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 532111 | Passenger Car Rental | Car Rental | `hospitality/travel/car-rental` |

---

## 54 - Professional, Scientific, and Technical Services

### 541 - Professional, Scientific, and Technical Services

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 541110 | Offices of Lawyers | Case Management | `professional-services/legal/case-management` |
| 541110 | Offices of Lawyers | Contract Lifecycle Management | `professional-services/legal/contract-lifecycle` |
| 541110 | Offices of Lawyers | Matter Management | `professional-services/legal/matter-management` |
| 541211 | Offices of Certified Public Accountants | Audit Management | `professional-services/accounting/audit-management` |
| 541211 | Offices of Certified Public Accountants | Client Accounting | `professional-services/accounting/client-accounting` |
| 541214 | Payroll Services | Payroll Processing | `professional-services/hr-services/payroll-processing` |
| 541330 | Engineering Services | Engagement Management | `engineering/consulting/engagement-management` |
| 541330 | Engineering Services | Knowledge Management | `engineering/consulting/knowledge-management` |
| 541330 | Engineering Services | Design Review | `engineering/product-development/design-review` |
| 541330 | Engineering Services | PLM Integration | `engineering/product-development/plm-integration` |
| 541330 | Engineering Services | Prototype Management | `engineering/product-development/prototype-management` |
| 541330 | Engineering Services | Design Review | `engineering/project-engineering/design-review` |
| 541330 | Engineering Services | Engineering Project | `engineering/project-engineering/engineering-project` |
| 541512 | Computer Systems Design Services | CI/CD Pipeline | `technology/devops/ci-cd-pipeline` |
| 541512 | Computer Systems Design Services | Deployment Pipeline | `technology/devops/deployment-pipeline` |
| 541512 | Computer Systems Design Services | Incident Management | `technology/devops/incident-management` |
| 541512 | Computer Systems Design Services | Infrastructure as Code | `technology/devops/infrastructure-as-code` |
| 541512 | Computer Systems Design Services | Observability | `technology/devops/observability` |
| 541614 | Process and Logistics Consulting | Demand Planning | `logistics/supply-chain/demand-planning` |
| 541614 | Process and Logistics Consulting | Supplier Management | `logistics/supply-chain/supplier-management` |
| 541714 | R&D in Biotechnology | Clinical Trials | `healthcare/life-sciences/clinical-trials` |
| 541810 | Advertising Agencies | Ad Operations | `marketing/advertising/ad-operations` |
| 541810 | Advertising Agencies | Campaign Management | `marketing/campaigns/campaign-management` |
| 541810 | Advertising Agencies | Email Marketing | `marketing/campaigns/email-marketing` |
| 541810 | Advertising Agencies | Marketing Automation | `marketing/campaigns/marketing-automation` |
| 541810 | Advertising Agencies | Content Management | `marketing/content/content-management` |
| 541810 | Advertising Agencies | Social Media Management | `marketing/social-media/social-management` |
| 541830 | Media Buying Agencies | Media Buying | `marketing/advertising/media-buying` |
| 541890 | Other Services Related to Advertising | Ad Serving | `marketing/advertising/ad-serving` |
| 541910 | Marketing Research and Public Opinion Polling | Attribution | `marketing/analytics/attribution` |
| 541910 | Marketing Research and Public Opinion Polling | Audience Management | `marketing/analytics/audience-management` |
| 541910 | Marketing Research and Public Opinion Polling | Marketing Analytics | `marketing/analytics/marketing-analytics` |

---

## 56 - Administrative and Support Services

### 561 - Administrative and Support Services

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 561311 | Employment Placement Agencies | Recruiting | `professional-services/hr-services/recruiting` |
| 561510 | Travel Agencies | Tour Operations | `hospitality/travel/tour-operations` |

---

## 61 - Educational Services

### 611 - Educational Services

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 611310 | Colleges, Universities, and Professional Schools | Course Management | `education/academic/course-management` |
| 611310 | Colleges, Universities, and Professional Schools | Learning Management System | `education/academic/learning-management` |
| 611310 | Colleges, Universities, and Professional Schools | Student Information System | `education/academic/student-information` |
| 611430 | Professional and Management Development Training | Competency Management | `education/corporate-training/competency-management` |
| 611430 | Professional and Management Development Training | Training Administration | `education/corporate-training/training-administration` |
| 611710 | Educational Support Services | Credentialing | `education/certification/credentialing` |

---

## 62 - Health Care and Social Assistance

### 621 - Ambulatory Health Care Services

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 621111 | Offices of Physicians | Appointment Scheduling | `healthcare/clinical/appointment-scheduling` |
| 621111 | Offices of Physicians | Care Coordination | `healthcare/clinical/care-coordination` |
| 621111 | Offices of Physicians | Clinical Encounter | `healthcare/clinical/clinical-encounter` |
| 621111 | Offices of Physicians | Patient Registration | `healthcare/clinical/patient-registration` |

### 622 - Hospitals

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 622110 | General Medical and Surgical Hospitals | Admission, Discharge, Transfer | `healthcare/hospitals/admission-discharge` |
| 622110 | General Medical and Surgical Hospitals | Lab Orders | `healthcare/hospitals/lab-orders` |
| 622110 | General Medical and Surgical Hospitals | Nursing Workflow | `healthcare/hospitals/nursing-workflow` |
| 622110 | General Medical and Surgical Hospitals | Operating Room | `healthcare/hospitals/operating-room` |
| 622110 | General Medical and Surgical Hospitals | Radiology Workflow | `healthcare/hospitals/radiology-workflow` |
| 622110 | General Medical and Surgical Hospitals | Hospital Supply Chain | `healthcare/hospitals/supply-chain` |

---

## 71 - Arts, Entertainment, and Recreation

### 711 - Performing Arts, Spectator Sports, and Related

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 711211 | Sports Teams and Clubs | Athlete Management | `entertainment/sports/athlete-management` |
| 711211 | Sports Teams and Clubs | League Management | `entertainment/sports/league-management` |
| 711211 | Sports Teams and Clubs | Team Management | `entertainment/sports/team-management` |
| 711310 | Promoters of Performing Arts and Similar Events | Production Management | `entertainment/live-events/production-management` |
| 711310 | Promoters of Performing Arts and Similar Events | Ticket Sales | `entertainment/live-events/ticket-sales` |
| 711310 | Promoters of Performing Arts and Similar Events | Ticketing | `entertainment/live-events/ticketing` |
| 711310 | Promoters of Performing Arts and Similar Events | Event Registration | `hospitality/events/event-registration` |
| 711310 | Promoters of Performing Arts and Similar Events | Venue Management | `hospitality/events/venue-management` |

---

## 72 - Accommodation and Food Services

### 721 - Accommodation

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 721110 | Hotels and Motels | Guest Services | `hospitality/lodging/guest-services` |
| 721110 | Hotels and Motels | Hotel Reservations | `hospitality/lodging/hotel-reservations` |
| 721110 | Hotels and Motels | Property Management | `hospitality/lodging/property-management` |
| 721110 | Hotels and Motels | Reservation System | `hospitality/lodging/reservation-system` |

### 722 - Food Services and Drinking Places

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 722320 | Caterers | Catering Management | `hospitality/food-service/catering-management` |
| 722511 | Full-Service Restaurants | Reactive BBQ | `hospitality/food-service/reactive-bbq` |
| 722511 | Full-Service Restaurants | Restaurant Operations | `hospitality/food-service/restaurant-operations` |

---

## 81 - Other Services (except Public Administration)

### 811 - Repair and Maintenance

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 811310 | Commercial and Industrial Machinery Repair | Asset Lifecycle | `manufacturing/maintenance/asset-lifecycle` |
| 811310 | Commercial and Industrial Machinery Repair | Equipment Maintenance | `manufacturing/maintenance/equipment-maintenance` |

---

## 92 - Public Administration

### 921 - Executive, Legislative, and General Government

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 921190 | Other General Government Support | Case Management | `government/citizen-services/case-management` |

### 922 - Justice, Public Order, and Safety Activities

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 922160 | Fire Protection | Emergency Dispatch | `government/public-safety/emergency-dispatch` |
| 922190 | Other Justice, Public Order, and Safety | Records Management | `government/public-safety/records-management` |

### 923 - Administration of Human Resource Programs

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 923130 | Administration of Human Resource Programs | Benefits Administration | `government/citizen-services/benefits-administration` |

### 926 - Administration of Economic Programs

| Code | Industry | Model | Path |
|------|----------|-------|------|
| 926150 | Regulation, Licensing, and Inspection | Permit Management | `government/citizen-services/permit-management` |
| 926150 | Regulation, Licensing, and Inspection | Compliance Reporting | `government/regulatory/compliance-reporting` |
| 926150 | Regulation, Licensing, and Inspection | Licensing | `government/regulatory/licensing` |
