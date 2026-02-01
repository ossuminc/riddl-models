# JSON Schemas

This directory contains JSON schemas for validating metadata files.

## Available Schemas

### model-metadata.schema.json

Validates `.metadata.json` files that accompany RIDDL models.

**Required fields:**
- `name` - Human-readable model name
- `description` - Brief description of the model

**Optional fields:**
- `author` - Creator of the model
- `version` - Semantic version (e.g., "1.0.0")
- `tags` - Keywords for discovery
- `difficulty` - Learning level: beginner, intermediate, advanced
- `complexity` - Implementation tier: starter, standard, enterprise
- `riddl_version` - Minimum compiler version required
- `simulation_ready` - Can run in riddlsim
- `related_patterns` - Patterns used in the model
- `related_models` - Links to related models
- `external_references` - External documentation links
- `industry_codes` - NAICS/SIC codes
- `license` - Model license (default: Apache-2.0)
- `created_at` / `updated_at` - ISO dates

## Validation

To validate a metadata file against the schema:

```bash
# Using ajv-cli
npx ajv validate -s schemas/model-metadata.schema.json -d path/to/model.metadata.json

# Using check-jsonschema
check-jsonschema --schemafile schemas/model-metadata.schema.json path/to/model.metadata.json
```

## Example

```json
{
  "name": "Shopping Cart",
  "description": "E-commerce shopping cart with add/remove/checkout",
  "author": "Ossum Inc.",
  "version": "1.0.0",
  "tags": ["e-commerce", "cart", "checkout", "beginner"],
  "difficulty": "beginner",
  "complexity": "standard",
  "riddl_version": "1.0.0",
  "simulation_ready": true,
  "related_patterns": ["entity/aggregate-root", "saga/distributed-transaction"]
}
```