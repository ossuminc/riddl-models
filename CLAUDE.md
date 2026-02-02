# CLAUDE.md - riddl-models

This file provides stable reference documentation for Claude Code when working
with the riddl-models repository.

**Important**: Read ../CLAUDE.md for general protocols and instructions on
working on Ossum Inc. project which are described in that file; this is one of
them.

## Project Overview

**riddl-models** is the canonical repository for example RIDDL models and
reusable patterns. It serves as a library for AI-assisted RIDDL development,
providing:

1. **Reusable Patterns** - DDD/Reactive patterns (event-sourced entity, saga,
   projector, etc.)
2. **Domain Examples** - Industry-specific RIDDL models organized by sector
3. **Best Practices** - Idioms, conventions, and anti-patterns documentation
4. **Metadata** - Structured metadata for model discovery and categorization

## Repository Structure

```
riddl-models/
├── patterns/                   # Reusable DDD/Reactive Patterns
│   ├── entity/                 # Aggregate patterns
│   ├── saga/                   # Distributed transaction patterns
│   ├── projection/             # CQRS read models
│   ├── gateway/                # API and integration patterns
│   └── workflow/               # Process orchestration patterns
│
├── technology/                 # Technology & SaaS
├── investment/                 # Investment & Venture Capital
├── finance/                    # Financial Services
├── insurance/                  # Insurance
├── commerce/                   # Retail & Commerce
├── hospitality/                # Accommodation & Food Service
├── entertainment/              # Arts, Entertainment & Media
├── marketing/                  # Marketing & Advertising
├── healthcare/                 # Healthcare & Life Sciences
├── manufacturing/              # Manufacturing & Production
├── construction/               # Construction & Real Estate
├── engineering/                # Engineering Services
├── transportation/             # Transportation (all modes)
├── logistics/                  # Supply Chain & Warehousing
├── natural-resources/          # Natural Resources & Mining
├── utilities/                  # Utilities & Energy
├── telecommunications/         # Telecommunications
├── government/                 # Government & Public Sector
├── education/                  # Education & Training
├── professional-services/      # Professional Services
│
├── schemas/                    # JSON Schemas for validation
│   └── model-metadata.schema.json
│
├── CLAUDE.md                   # This file
├── NOTEBOOK.md                 # Development journal
└── README.md                   # Project documentation
```

---

## Domain Ontology

The repository organizes models into **18 top-level sectors** covering
enterprise, SMB, and startup needs. Each sector has 2-5 subsectors, with
individual models at level 3.

### Sectors Overview

| Sector | Description | Key Subsectors |
|--------|-------------|----------------|
| `technology` | Technology & SaaS | saas, devops, platform |
| `investment` | Investment & Venture Capital | venture-capital, private-equity, asset-management |
| `finance` | Financial Services | banking, payments, trading |
| `insurance` | Insurance | property-casualty, life-annuity, reinsurance |
| `commerce` | Retail & Commerce | e-commerce, retail, marketplace, wholesale |
| `hospitality` | Accommodation & Food Service | lodging, food-service, travel, events |
| `entertainment` | Arts, Entertainment & Media | media, gaming, live-events, sports |
| `marketing` | Marketing & Advertising | campaigns, advertising, analytics |
| `healthcare` | Healthcare & Life Sciences | hospitals, clinical, pharmacy, payer, life-sciences |
| `manufacturing` | Manufacturing & Production | discrete, process, machining, textiles, maintenance |
| `construction` | Construction & Real Estate | project-management, field-operations, real-estate |
| `engineering` | Engineering Services | project-engineering, product-development, consulting |
| `transportation` | Transportation (all modes) | freight, passenger, fleet, maritime |
| `logistics` | Supply Chain & Warehousing | warehousing, fulfillment, supply-chain |
| `natural-resources` | Natural Resources & Mining | mining, oil-gas, forestry, agriculture |
| `utilities` | Utilities & Energy | electric, gas, water, metering |
| `telecommunications` | Telecommunications | network, billing, customer |
| `government` | Government & Public Sector | citizen-services, regulatory, public-safety |
| `education` | Education & Training | academic, corporate-training, certification |
| `professional-services` | Professional Services | legal, accounting, hr-services |

---

## Model File Structure

Each model directory contains:

```
commerce/e-commerce/shopping-cart/
├── shopping-cart.riddl           # The RIDDL model
├── shopping-cart.metadata.json   # Model metadata (optional)
└── README.md                     # Human-readable explanation
```

### Metadata Schema

Model metadata files follow this structure:

```json
{
  "name": "Shopping Cart",
  "description": "E-commerce shopping cart with add/remove/checkout",
  "author": "Ossum Inc.",
  "version": "1.0.0",
  "tags": ["e-commerce", "cart", "checkout", "beginner"],
  "difficulty": "beginner",
  "riddl_version": "1.0.0",
  "simulation_ready": true,
  "related_patterns": ["entity/event-sourced", "saga/checkout"],
  "complexity": "standard"
}
```

#### Complexity Tiers

Models can include a `complexity` field to indicate suitability:

| Tier | Description |
|------|-------------|
| `starter` | Simplified version for SMB (fewer entities, basic workflows) |
| `standard` | Full-featured for mid-market |
| `enterprise` | Advanced features, integrations, compliance |

---

## Patterns Directory

The `patterns/` directory contains reusable RIDDL pattern templates:

### Available Patterns

| Pattern | Directory | Description |
|---------|-----------|-------------|
| Event-Sourced Entity | `entity/event-sourced/` | Entity persisting changes as events |
| Aggregate Root | `entity/aggregate-root/` | Entity managing child entities |
| Saga | `saga/distributed-transaction/` | Multi-step process with compensation |
| Repository | `entity/repository/` | Persistence and query capabilities |
| Projector | `projection/read-model/` | CQRS read-optimized views |
| Process Manager | `workflow/process-manager/` | Event-driven workflow coordination |

Each pattern includes:
- `template.riddl` - Parameterized RIDDL template with `{Placeholders}`
- `README.md` - When to use, how to customize
- `example.riddl` - Concrete example instantiation

---

## Conventions

### File Naming

- RIDDL files: `kebab-case.riddl` (e.g., `shopping-cart.riddl`)
- Metadata files: Match RIDDL filename with `.metadata.json` suffix
- README files: Always `README.md` (uppercase)

### RIDDL Style

Follow these idioms when writing RIDDL:

1. **Use `is` keyword** for readability: `entity Order is { }`
2. **Use `???` for placeholders** - empty bodies not allowed
3. **Commands use imperative** - `CreateOrder`, `ShipProduct`
4. **Events use past tense** - `OrderCreated`, `ProductShipped`
5. **Always add `briefly`** descriptions
6. **Use explicit states** - avoid flag-based state machines
7. **Type IDs as `{Name}Id`** - `type OrderId is Id(Order)`

### RIDDL Syntax Reference

**Description Syntax** - Three valid forms for `described by`:

```riddl
// Form 1: Simple quoted string (best for short descriptions)
described by "A short description."

// Form 2: Multiple quoted strings in braces
described by { "Line one." "Line two." "Line three." }

// Form 3: Markdown with pipe character (MUST have } on separate line)
described by {
  | Markdown line one.
  | Markdown line two.
}
```

**CRITICAL**: The `|` character consumes everything to end of line including
any `}` on the same line. This is WRONG: `described by { | Text here. }`

**Naming Collision Avoidance**:
- Enum values and state names in the same scope cannot match
- Use suffixes like `State` or `Status` to disambiguate
- Example: enum `DeliveryFailed` vs state `DeliveryFailedState`

**External Contexts**:
- Mark external bounded contexts with `option is external` in the `with` block
- NOT inside the context body

```riddl
context PaymentGateway is {
  // events and types only, no handlers
} with {
  option is external
  briefly "External payment processing system"
}
```

**Messaging**:
- Use `tell event X to entity Y` for entity-to-entity messaging
- Use `tell command X to entity Y` for command dispatch
- `send to outlet` is only for streamlet flows

**State Transitions**:
- Use `morph entity X to state Y with command Z` for state changes
- The `with command` provides the data source for the new state

### Directory Naming

- Sectors: `kebab-case` (e.g., `natural-resources`)
- Subsectors: `kebab-case` (e.g., `oil-gas`)
- Models: `kebab-case` (e.g., `well-management`)

---

## Validation with riddlc

**Use `riddlc` directly for validation** - it handles includes properly and
provides clear error messages. The MCP server can still be used for other
purposes like querying grammar, idioms, and patterns.

### Setup

Each model directory should have a `.conf` file:

```hocon
validate {
  input-file = "model-name.riddl"
}
```

### Validation Command

```bash
# From the model directory
/path/to/riddlc from model-name.conf validate
```

The riddlc binary is typically at:
`riddl/riddlc/jvm/target/universal/stage/bin/riddlc`

### Model File Structure

Break models into separate files using `include`:

```
model-directory/
├── model-name.conf           # riddlc configuration
├── model-name.riddl          # Domain entry point with includes
├── types.riddl               # Shared types
├── Entity1.riddl             # Entity definitions
├── Entity2.riddl
├── Context.riddl             # Main bounded context
├── external-contexts.riddl   # External systems (option is external)
└── README.md
```

The main `.riddl` file uses `include "filename.riddl"` to compose the model.

---

## Contributing Models

### Adding a New Model

1. Choose the appropriate sector and subsector
2. Create a directory: `sector/subsector/model-name/`
3. Create the configuration file: `model-name.conf`
4. Add the main RIDDL file: `model-name.riddl`
5. Break into separate files using `include` for types, entities, contexts
6. Add README.md explaining the model's purpose
7. Validate with `riddlc from model-name.conf validate`
8. Optionally add metadata: `model-name.metadata.json`

### Model Quality Checklist

- [ ] Has `model-name.conf` for riddlc validation
- [ ] All definitions have `briefly` descriptions
- [ ] All definitions have `described by` for longer descriptions
- [ ] Commands use imperative naming
- [ ] Events use past tense naming
- [ ] States are explicit (not flag-based)
- [ ] No naming collisions between enum values and state names
- [ ] Handlers have implementation or `???`
- [ ] Types are domain-specific (not generic `String`)
- [ ] Sagas have compensation logic
- [ ] Validates with `riddlc` (0 errors)

---

## Integration with riddl-mcp-server

Models in this repository are designed to work with the riddl-mcp-server tools:

- `validate-text` / `validate-url` - Validate model syntax and semantics
- `validate-partial` - Validate incomplete models during development
- `check-completeness` - Find missing elements
- `check-simulability` - Verify model can run in riddlsim
- `expand-pattern` - Generate code from patterns in this repo

---

## Related Projects

- **riddl** - RIDDL language compiler and tooling
- **riddl-mcp-server** - MCP server using these models as resources
- **riddlsim** - Simulation engine for RIDDL models
- **synapify** - Visual editor for RIDDL

---

## Version Compatibility

| riddl-models | RIDDL Compiler | MCP Server |
|--------------|----------------|------------|
| 1.0.x | 1.0.x | 0.3.x |

Models are validated against the RIDDL grammar using the latest stable compiler.
