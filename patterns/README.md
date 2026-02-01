# Reusable RIDDL Patterns

This directory contains reusable DDD/Reactive patterns for RIDDL domain
modeling. Each pattern provides a parameterized template that can be customized
for your specific domain.

## Pattern Categories

| Directory | Focus |
|-----------|-------|
| `entity/` | Aggregate patterns (event-sourced, aggregate root, repository) |
| `saga/` | Distributed transaction patterns with compensation |
| `projection/` | CQRS read models and views |
| `gateway/` | API and external integration patterns |
| `workflow/` | Process orchestration and state machines |

## Using Patterns

1. Choose a pattern that fits your use case
2. Copy the `template.riddl` file
3. Replace `{Placeholders}` with your domain-specific names
4. Customize fields, commands, and events for your needs

## Pattern Selection Guide

| Need | Pattern |
|------|---------|
| Full audit trail | `entity/event-sourced` |
| Parent-child relationships | `entity/aggregate-root` |
| Entity persistence | `entity/repository` |
| Multi-step transactions | `saga/distributed-transaction` |
| Read-optimized queries | `projection/read-model` |
| External API facade | `gateway/api-gateway` |
| Event-driven workflows | `workflow/process-manager` |

## Template Syntax

Patterns use `{Placeholders}` for customization:

```riddl
entity {EntityName} is {
  type {EntityName}Id is Id({EntityName})

  command Create{EntityName} is {
    id: {EntityName}Id
    // TODO: Add fields
  }

  event {EntityName}Created is {
    id: {EntityName}Id,
    createdAt: TimeStamp
  }
}
```

Replace `{EntityName}` with your actual name (e.g., `Order`, `Customer`).