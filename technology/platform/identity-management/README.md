# Identity Management

Authentication, authorization, and SSO.

## Overview

This model manages user identities, authentication methods, authorization
policies, and single sign-on integration.

## Key Entities

- **Identity** - User or service account
- **Credential** - Authentication method
- **Permission** - Authorization grant

## Commands

- `CreateIdentity` - Register new user
- `AddCredential` - Add auth method
- `GrantPermission` - Authorize access
- `RevokePermission` - Remove access
- `Authenticate` - Verify identity

## Events

- `IdentityCreated` - User registered
- `CredentialAdded` - Auth method added
- `PermissionGranted` - Access authorized
- `AuthenticationSucceeded` - Login successful
- `AuthenticationFailed` - Login failed

## Integration Points

- SSO providers (SAML, OIDC)
- Directory services (LDAP, AD)
- MFA providers
- Audit logging