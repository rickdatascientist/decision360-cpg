# Security model and limitations

## Protected assets and trust boundaries

The protected assets are decision inputs, recommendations, human decisions, realized outcomes, API credentials, and the audit chain. The browser, ingress, application process, SQLite file, backup destination, and future agent adapter are separate trust boundaries.

## Implemented controls

- API-key authentication configured only through the environment;
- distinct operator, approver, viewer, auditor, and admin roles;
- constant-time token comparison and fail-closed invalid configuration;
- separate human approval endpoint; governed tools cannot approve, record outcomes, or perform external writes;
- idempotency keys and request hashes for evaluation and outcome writes;
- transactional persistence, foreign keys, and approval-before-outcome enforcement;
- hash-chained audit events with an integrity endpoint;
- non-root container execution and no committed runtime secret;
- synthetic public examples only.

## Known limitations

This reference does not provide user federation, token expiry, tenant isolation, field-level encryption, a network ingress, rate limiting, centralized logs, managed key rotation, high availability, or a managed database. API keys are bearer secrets. SQLite is single-instance storage. These limitations block a claim of production readiness.

## Deployment requirements

For shared deployment, use TLS at ingress, a secret manager, network allow-lists, request/body limits, rate limiting, encrypted persistent storage and backups, centralized immutable logs, vulnerability scanning, and an incident owner. Replace API-key authentication with workload/user identity before multi-user production use.

## Reporting

Do not open a public issue containing credentials, private data, or exploitable details. Use the repository owner's private security-reporting channel. Public test fixtures must remain synthetic and sanitized.
