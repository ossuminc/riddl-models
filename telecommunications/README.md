# Telecommunications

RIDDL models for network operations, billing, and subscriber management.

## Subsectors

### network/
Network provisioning and operations.

**Models:**
- `service-provisioning/` - Order, configure, activate
- `network-operations/` - Monitoring, faults, performance

### billing/
Usage rating and revenue management.

**Models:**
- `usage-rating/` - CDRs, mediation, rating
- `revenue-assurance/` - Leakage detection, reconciliation

### customer/
Subscriber and account management.

**Models:**
- `subscriber-management/` - Accounts, plans, devices

## Common Patterns

Telecom models frequently use:
- High-throughput event streams for CDRs
- Multi-state entities for subscriber lifecycle
- Saga patterns for provisioning workflows
- Projectors for real-time usage dashboards

## Domain-Specific Concepts

- **CDR** - Call Detail Record
- **OSS/BSS** - Operations/Business Support Systems
- **NNI** - Network-Network Interface
- **SIM/eSIM** - Subscriber Identity Module