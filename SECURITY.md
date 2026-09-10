# Security Policy

## Supported version

Security fixes target the latest v1.x release.

## Reporting

Please report vulnerabilities privately through GitHub Security Advisories. Do not include secrets,
customer data, or exploit payloads in public issues.

## Deployment requirements

- Replace every example password and secret before starting the stack.
- Use at least 32 random bytes for `JWT_SECRET`.
- Rotate `BOOTSTRAP_SECRET` after creating the first administrator.
- Terminate TLS at a trusted reverse proxy and restrict `CORS_ORIGINS`.
- Keep PostgreSQL, Redis, and Prometheus endpoints on private networks.
- Use a least-privilege provider key and never commit it.
- Review every MCP tool's `requires_approval` classification.
- Back up PostgreSQL and test restoration regularly.

Containers run as non-root with `no-new-privileges`. Images should be scanned and pinned by digest
in regulated deployments.
