# API Gateway Pattern

Provides a unified API facade for external clients, aggregating and routing
requests to multiple internal contexts.

## When to Use

- Need a single entry point for external clients
- Want to aggregate responses from multiple contexts
- Require protocol translation or rate limiting
- Hide internal service complexity from clients

## Template Parameters

| Parameter | Description |
|-----------|-------------|
| `{GatewayName}` | The gateway name (e.g., `PublicAPI`, `MobileAPI`) |

## Key Elements

- **Context**: The gateway is its own bounded context
- **Router Entity**: Routes requests to internal contexts
- **Adaptor**: Translates between external and internal protocols

## Responsibilities

- Request routing
- Response aggregation
- Protocol translation
- Authentication/Authorization
- Rate limiting
- Request validation

## Usage

1. Copy `template.riddl`
2. Replace `{GatewayName}` with your gateway name
3. Define request/response types
4. Implement routing logic in handler
5. Add adaptors for external integrations