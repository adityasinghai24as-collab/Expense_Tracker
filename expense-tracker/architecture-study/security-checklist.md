# Application Security Deployment Checklist (Merged)
### Industry-Standard Hardening Guide (OWASP ASVS / CIS Benchmarks / NIST-aligned)

> **Reality check:** No checklist makes a system "unhackable." This one closes 95%+ of real-world attack paths and ensures that if something does slip through, you detect and contain it fast.
> **For Expense Tracker**: We target **OWASP ASVS Level 2** as our baseline. Items marked with ⭐ are specific high-priority implementations mapped to our project.

## 1. Authentication & Authorization
- **Strong authentication**: Use OAuth 2.0/OIDC or JWT with short expiry + refresh tokens (avoid long-lived tokens).
- **Multi-factor authentication (MFA)** for sensitive accounts/actions (offer TOTP/WebAuthn).
- ⭐ **Least privilege / RBAC**: Every endpoint checks role/permission, not just "is logged in".
- **Object-level authorization**: Verify the requesting user actually owns/can access the specific resource (prevents IDOR).
- ⭐ **Secure session management**: HttpOnly, Secure, SameSite cookies; invalidate sessions server-side on logout/password change. Implement absolute and idle session timeouts, and rotate session identifiers to prevent fixation.
- ⭐ **Password Policy**: Enforce strong password policy (min 12 chars, checked against Pwned Passwords API). Hash with Argon2id or bcrypt (cost ≥ 12).
- **Password Reset**: Implement time-limited, single-use tokens sent via verified channel only.

## 2. Rate Limiting & Abuse Prevention
- **Rate limiting**: Per-IP and per-user/per-API-key rate limiting (sliding window or token bucket).
- **Stricter limits** on sensitive endpoints (login, password reset, OTP, search).
- ⭐ **Lockouts**: Exponential backoff / temporary lockouts after repeated failed logins.
- **CAPTCHA or proof-of-work** on high-abuse endpoints.
- **WAF/Gateway**: Use a gateway/WAF (Cloudflare, AWS API Gateway) rather than hand-rolling this in app code. Layer 3/4 DDoS protection.
- **Request Limits**: Set request size limits (body, header, upload) to prevent resource exhaustion.

## 3. Injection Prevention
- ⭐ **SQL Injection**: Always use parameterized queries/prepared statements or an ORM (e.g., SQLAlchemy) — never string-concatenate SQL.
- **NoSQL Injection**: Sanitize inputs; avoid passing raw user input into query operators.
- **Command Injection**: Never pass user input to shell commands; use safe APIs instead of exec/system.
- **Input validation**: Whitelist expected formats (type, length, range, regex) at the API boundary.
- **File Uploads**: Validate MIME type + magic bytes (not just extension), enforce size limits, store outside webroot, and scan with ClamAV.
- **Deserialization**: Disable dangerous deserialization of untrusted data (e.g., Python `pickle`).
- **SSRF Prevention**: Validate outbound URLs, block requests to internal IP ranges (169.254.x.x, 10.x, 192.168.x).

## 4. Data Validation & Sanitization
- **Server-side Validation**: Validate on the server (client-side validation is UX only, not security).
- ⭐ **Schema Validation**: Use schema validation libraries (e.g., Pydantic) to reject unexpected fields (mass assignment protection).
- **Sanitize output**: Prevent stored XSS if data is later rendered by escaping contextually.
- **Data Protection**: Encrypt sensitive data at rest (TDE) and backup. Never log sensitive data (PII, tokens) in plaintext.

## 5. Transport & Infrastructure Security
- ⭐ **Enforce HTTPS everywhere**: TLS 1.2+ only (prefer 1.3), disable weak ciphers, use HSTS with `includeSubDomains` and `preload`.
- ⭐ **Secure headers**: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, and `Permissions-Policy` (disable camera/mic).
- **CORS**: Strict CORS policy — explicit allowlist of origins, don't use `*` with credentials.
- **Network Segmentation**: Isolate public-facing, app, and database tiers in separate subnets. DB should never be directly reachable from the public internet.
- **OS Hardening**: Harden OS images against CIS Benchmarks; use minimal base images (distroless/Alpine).

## 6. API-Specific Hardening
- **Secrets Management**: API keys/secrets never in URLs (use headers).
- **Versioning**: Versioned APIs so you can deprecate insecure endpoints.
- ⭐ **Error Handling**: Return generic error messages externally; log detailed errors internally. Disable verbose error messages/stack traces in production.
- ⭐ **Pagination limits**: Enforce limits on list endpoints to prevent data scraping/resource exhaustion.

## 7. Secrets & Config Management
- ⭐ **No secrets in code**: Zero secrets in source control — enforce with pre-commit hooks (gitleaks).
- **Secrets Manager**: Use env vars or a secrets manager (Vault, AWS Secrets Manager).
- **Rotation**: Rotate API keys/credentials periodically.
- **Environment Isolation**: Separate credentials per environment (dev/staging/prod).

## 8. Logging, Monitoring & Response
- ⭐ **Centralized logging**: Log auth failures, rate-limit hits, 4xx/5xx spikes, and admin actions.
- **Alerting**: Set real-time alerts for anomalous patterns (sudden traffic spikes, privilege escalation).
- **Audit logs**: Track sensitive actions (who did what, when), including DB schema changes.
- **Incident Response Plan**: Have a written incident response plan, breach notification templates, and conduct tabletop exercises.
- **Uptime Monitoring**: Set up uptime/synthetic monitoring plus error-rate/latency alerting.

## 9. Dependency & Infra Hygiene
- ⭐ **Regular scanning**: SAST/SCA scanning in CI (npm audit, pip-audit, Snyk/Dependabot).
- **Container security**: Scan container images (Trivy), run as non-root users, use read-only root filesystems, set resource limits.
- **CI/CD Security**: Require signed commits, branch protection, and manual deployment approval gates.
- **Least privilege**: Principle of least privilege for cloud IAM roles, DB users, and CI/CD scoped credentials.
- **Patch Management**: Keep frameworks/libraries/OS patched on an automated schedule.

## 10. Additional Defenses
- **CSRF protection**: For cookie-based sessions (SameSite=Strict).
- **Idempotency keys**: For payment/critical write endpoints.
- **Regular security testing**: Automated SAST/DAST scans, periodic manual penetration testing, and fuzz-testing critical parsers.
- **Secure SDLC**: Threat model the application (STRIDE) before major feature work. Maintain a Software Bill of Materials (SBOM).
- **Disaster Recovery**: Automated encrypted backups, immutable backups (against ransomware), and periodic DR drills (RTO/RPO).
- **Compliance**: Map controls to GDPR, CCPA, SOC 2, and maintain a data processing inventory.

## 11. Quality Assurance & Performance Testing
- ⭐ **Automated Unit & Integration Testing**: Achieve high test coverage for all critical paths (e.g., via `pytest` for backend, `Jest`/`Vitest` for frontend). Ensure tests are run automatically in the CI pipeline.
- ⭐ **Load & Stress Testing**: Conduct periodic load tests (using tools like `Locust`, `k6`, or `JMeter`) to identify performance bottlenecks, DoS limits, and optimize database connection pooling.
- **End-to-End (E2E) Testing**: Simulate actual user journeys (e.g., via `Playwright` or `Cypress`) to verify that the frontend and backend integrate securely and correctly.
- **Chaos Engineering**: Introduce controlled faults (e.g., dropping DB connections) to ensure graceful degradation and resilience.
- **Contract Testing**: Verify that frontend and backend expectations (API schemas) do not break during deployments.
