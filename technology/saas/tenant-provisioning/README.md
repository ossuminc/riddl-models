# Tenant Provisioning

New customer onboarding and environment setup.

## NAICS Code

**511210** - Software Publishers

## Overview

This model handles provisioning of new SaaS tenants including environment
creation, configuration, and initial setup.

## Key Entities

- **Tenant** - Customer organization
- **Environment** - Tenant's isolated instance
- **Configuration** - Tenant-specific settings

## Commands

- `CreateTenant` - Start provisioning
- `ConfigureEnvironment` - Apply settings
- `ActivateTenant` - Enable access
- `DecommissionTenant` - Remove tenant
- `MigrateTenant` - Move to different infrastructure

## Events

- `TenantCreated` - Provisioning started
- `EnvironmentReady` - Infrastructure ready
- `TenantActivated` - Tenant can access
- `TenantDecommissioned` - Tenant removed
- `TenantMigrated` - Successfully moved

## Integration Points

- Infrastructure automation
- Identity management
- Subscription management
- Data migration tools