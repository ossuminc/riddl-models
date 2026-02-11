# Infrastructure as Code

IaC state management, provisioning, and drift detection.

## NAICS Code

**541512** - Computer Systems Design Services

## Overview

This model manages infrastructure as code stacks including planning,
applying changes, drift detection, and resource lifecycle across
cloud providers.

## Key Entities

- **Stack** - Infrastructure stack with resources and state

## Commands

- `CreateStack` - Define new infrastructure stack
- `PlanStack` - Generate execution plan
- `ApplyStack` - Apply infrastructure changes
- `DetectDrift` - Check for configuration drift
- `ReconcileDrift` - Fix drifted resources
- `UpdateVariables` - Update stack variables
- `DestroyStack` - Destroy all stack resources
- `LockStack` - Lock stack from changes
- `UnlockStack` - Unlock stack for changes

## Events

- `StackCreated` - Stack defined
- `PlanGenerated` - Execution plan ready
- `StackApplyStarted` - Apply in progress
- `StackApplyCompleted` - Apply finished
- `DriftDetected` - Configuration drift found
- `DriftReconciled` - Drift corrected
- `VariablesUpdated` - Variables changed
- `StackDestroyed` - Resources destroyed
- `StackLocked` - Stack locked
- `StackUnlocked` - Stack unlocked

## Integration Points

- Cloud providers (AWS, Azure, GCP)
- State backends (S3, GCS, Consul)
- Secret managers (Vault, AWS Secrets Manager)
- Module registries (Terraform Registry)
- Policy engines (Sentinel, OPA)
