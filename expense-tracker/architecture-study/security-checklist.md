# Application Security Deployment Checklist
### Industry-Standard Hardening Guide (OWASP ASVS / CIS Benchmarks / NIST-aligned)

> **Reality check:** No checklist makes a system "unhackable." This one closes 95%+ of real-world attack paths (per OWASP Top 10 + Verizon DBIR breach patterns) and ensures that if something does slip through, you detect and contain it fast. Security is a process, not a one-time deployment gate.

> **For Expense Tracker**: We target **OWASP ASVS Level 2** as our baseline. Items marked with ⭐ are implemented or planned in specific TODO.md phases.

---

## 1. Secure SDLC (Before You Write Code)

- [ ] Threat model the application (STRIDE or attack-tree) before major feature work
- [ ] Define a security baseline: which OWASP ASVS level (1/2/3) you're targeting → **Level 2**
- [ ] ⭐ Enforce mandatory code review with a security-focused checklist for every PR → *Phase 9 (CI/CD)*
- [ ] ⭐ Run SAST (Static Application Security Testing) in CI — e.g., Semgrep, SonarQube, CodeQL → *Phase 9*
- [ ] ⭐ Run SCA (Software Composition Analysis) — e.g., Dependabot, Snyk, OWASP Dependency-Check → *Phase 9*
- [ ] Establish a private, documented vulnerability disclosure / bug bounty process
- [ ] Maintain a Software Bill of Materials (SBOM) for every release

---

## 2. Secrets & Credentials Management

- [ ] ⭐ **Zero secrets in source control** — enforce with pre-commit hooks (git-secrets, gitleaks) and CI scanning → *`.gitignore` configured, Phase 9 for CI scanning*
- [ ] Use a dedicated secrets manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Doppler) — never `.env` files in production → *Phase 7 (Deployment)*
- [ ] Rotate all secrets (API keys, DB passwords, JWT signing keys) on a fixed schedule (e.g., 90 days) and immediately on suspected compromise
- [ ] Use short-lived, auto-rotating credentials (IAM roles, OIDC federation) instead of static keys wherever possible
- [ ] ⭐ Separate secrets per environment (dev/staging/prod) — never reuse prod secrets in lower environments → *Done: `config/.env.development`, `.env.val`, `.env.prod`*
- [ ] Encrypt secrets at rest with envelope encryption (KMS-backed)
- [ ] Audit every secret access (who/when/what) via the secrets manager's logging

---

## 3. Authentication & Authorization

- [ ] ⭐ Enforce strong password policy (min 12 chars, checked against breach corpuses like HaveIBeenPwned's Pwned Passwords API — **not** arbitrary complexity rules) → *Phase 3, Task 12*
- [ ] ⭐ Hash passwords with **Argon2id** (preferred) or bcrypt (cost factor ≥ 12) — never MD5/SHA1/plain SHA256 → *Phase 3, Task 12 (bcrypt via passlib)*
- [ ] Enforce MFA for all privileged/admin accounts; offer TOTP/WebAuthn for all users
- [ ] ⭐ Implement account lockout / exponential backoff on repeated failed logins → *Phase 3, Task 14*
- [ ] Use OAuth2/OIDC for third-party auth (never roll your own SSO)
- [ ] ⭐ Implement **Principle of Least Privilege** — every service account/role gets the minimum permissions needed → *Phase 4 (CRUD) + Phase 10 (Enterprise)*
- [ ] ⭐ Enforce Role-Based (RBAC) or Attribute-Based (ABAC) access control on every endpoint — never trust client-side role checks alone → *Phase 4*
- [ ] ⭐ Re-validate authorization server-side on every request (don't cache "is admin" in a JWT claim without expiry/revocation checks) → *Phase 3, Task 13*
- [ ] ⭐ Implement secure password reset flow: time-limited, single-use tokens sent via verified channel only → *Phase 3 stretch*

---

## 4. Input Validation & Injection Prevention (OWASP Top 10)

- [ ] ⭐ **Parameterized queries / ORM only** — zero string-concatenated SQL, ever → *Done: SQLAlchemy ORM throughout*
- [ ] ⭐ Validate and sanitize all input server-side (never trust client-side validation alone) → *Done: Pydantic schemas validate all inputs*
- [ ] Use allowlist validation (accept known-good patterns) over denylist (block known-bad)
- [ ] Escape output contextually (HTML, JS, URL, SQL, shell) to prevent XSS
- [ ] Sanitize file uploads: validate MIME type + magic bytes (not just extension), enforce size limits, store outside webroot, scan with antivirus (ClamAV) before serving
- [ ] Disable dangerous deserialization of untrusted data (e.g., Python `pickle`, Java native serialization)
- [ ] Prevent SSRF: validate/allowlist outbound URLs, block requests to internal IP ranges (169.254.x.x, 10.x, 172.16-31.x, 192.168.x) from server-side fetch functions
- [ ] Prevent command injection: avoid shell execution with user input; if unavoidable, use argument arrays, never string interpolation
- [ ] Set strict Content-Type validation and reject unexpected payload types

---

## 5. API Security

- [ ] ⭐ Authenticate every API endpoint (no "hidden" unauthenticated internal routes) → *Phase 3, Task 13 (`get_current_user` dependency)*
- [ ] ⭐ Version your API and deprecate old versions on a schedule → *Phase 4 (prefix `/api/v1/`)*
- [ ] ⭐ Implement schema validation (JSON Schema / Pydantic) on all request bodies → *Done: Pydantic schemas*
- [ ] ⭐ Return generic error messages externally; log detailed errors internally (never leak stack traces to clients) → *Phase 4, Task 4.3*
- [ ] ⭐ Implement pagination limits — prevent unbounded data dumps via a single query → *Phase 4, Task 4.2*
- [ ] ⭐ Rate-limit per API key/user/IP, not just globally → *Phase 10 (Enterprise)*
- [ ] Use API gateways for centralized auth, rate limiting, and logging

---

## 6. Data Protection & Encryption

- [ ] ⭐ TLS 1.2+ enforced everywhere (prefer 1.3); disable TLS 1.0/1.1 and all SSL versions → *Phase 7 (Cloud Run provides HTTPS automatically)*
- [ ] ⭐ HSTS enabled with `includeSubDomains` and `preload` → *Phase 7*
- [ ] Encrypt sensitive data at rest (AES-256) — DB-level (TDE) or column-level for PII/financial data
- [ ] Encrypt backups with keys separate from the data they protect
- [ ] Classify data (public/internal/confidential/restricted) and apply controls per class
- [ ] Implement field-level encryption or tokenization for highly sensitive data (SSNs, card numbers, health data)
- [ ] ⭐ Never log sensitive data (passwords, tokens, PII) in plaintext — mask/redact in logs → *Phase 10 (structured logging)*
- [ ] Define and enforce data retention/deletion policies (GDPR/CCPA "right to erasure" support)

---

## 7. Network & Infrastructure Security

- [ ] Default-deny firewall rules; explicitly allowlist only required ports/IPs
- [ ] ⭐ Segment networks: public-facing tier, application tier, and database tier in separate subnets with no direct DB internet exposure → *Done: Docker bridge network isolates DB*
- [ ] Put a Web Application Firewall (WAF) in front of the app (Cloudflare, AWS WAF, ModSecurity)
- [ ] Use a CDN to absorb volumetric traffic and hide origin IPs
- [ ] Disable unused ports, services, and protocols on every host
- [ ] Enforce infrastructure-as-code (Terraform/Pulumi) with policy-as-code scanning (Checkov, tfsec) before apply
- [ ] ⭐ Harden OS images against CIS Benchmarks; use minimal base images (distroless/Alpine) for containers → *Done: `python:3.11-slim` and `postgres:15-alpine`*
- [ ] Patch OS and dependencies on an automated schedule (unattended-upgrades / patch management tooling)

---

## 8. Container & Orchestration Security

- [ ] ⭐ Run containers as non-root users → *TODO: Add `USER` directive to backend Dockerfile*
- [ ] ⭐ Use read-only root filesystems where possible → *TODO: Add `read_only: true` in docker-compose.yml*
- [ ] ⭐ Scan container images for vulnerabilities (Trivy, Grype) in CI before push → *Phase 9 (CI/CD)*
- [ ] Sign and verify image provenance (Cosign/Sigstore)
- [ ] ⭐ Set resource limits (CPU/memory) to prevent noisy-neighbor/DoS via resource exhaustion → *TODO: Add to docker-compose.yml*
- [ ] Enforce Kubernetes NetworkPolicies (default-deny between pods) — *applicable when scaling to K8s*
- [ ] Use Pod Security Standards (restricted profile) — no privileged containers, no host namespace sharing
- [ ] Rotate service account tokens; disable auto-mounting where not needed

---

## 9. CI/CD Pipeline Security

- [ ] ⭐ Require signed commits and branch protection rules (no direct push to `main`) → *Phase 9*
- [ ] ⭐ Require passing security scans (SAST/SCA/secret scan) as a merge gate, not just a warning → *Phase 9*
- [ ] Use short-lived, scoped credentials for CI/CD to cloud providers (OIDC federation, not static keys)
- [ ] Isolate build environments — untrusted PRs (e.g., from forks) should not have access to secrets
- [ ] Sign build artifacts and verify signatures before deployment
- [ ] ⭐ Implement deployment approval gates for production releases → *Phase 9*
- [ ] Maintain immutable, auditable deployment history (who deployed what, when)

---

## 10. Logging, Monitoring & Alerting

- [ ] ⭐ Centralize logs (ELK, Datadog, CloudWatch, Grafana Loki) — never rely on local log files only → *Phase 10*
- [ ] ⭐ Log all authentication events, authorization failures, and admin actions → *Phase 3 + Phase 10*
- [ ] Set real-time alerts for anomalies: repeated auth failures, privilege escalation, unusual data export volume, geographic anomalies
- [ ] Implement intrusion detection (IDS/IPS) or a SIEM correlating logs across services
- [ ] Monitor dependency vulnerability feeds continuously (not just at build time)
- [ ] Ensure logs are tamper-evident (write-once storage or hash-chained) and retained per compliance requirements
- [ ] ⭐ Set up uptime/synthetic monitoring plus error-rate/latency alerting (Sentry, Prometheus) → *Phase 10*

---

## 11. Session Management

- [ ] ⭐ Generate session tokens with a cryptographically secure RNG, sufficient entropy (128+ bits) → *Phase 3, Task 12 (python-jose uses secure RNG)*
- [ ] ⭐ Set cookies with `HttpOnly`, `Secure`, and `SameSite=Strict` (or `Lax` if cross-site flows are needed) → *Phase 3, Task 14*
- [ ] ⭐ Implement absolute and idle session timeouts → *Phase 3, Task 12 (token expiry)*
- [ ] ⭐ Invalidate sessions server-side on logout (don't rely on client-side token deletion alone) → *Phase 3, Task 14 (clear refresh_token in DB)*
- [ ] ⭐ Rotate session identifiers after login (prevent session fixation) → *Phase 3, Task 14 (new tokens on each login)*
- [ ] ⭐ For JWTs: use short expiry + refresh token rotation, support revocation (blocklist or short-lived access tokens), never store sensitive data in the payload → *Phase 3 design*

---

## 12. Security Headers (Browser-Side Protections)

- [ ] ⭐ `Content-Security-Policy` — restrict script/style/img sources, disable inline scripts where feasible → *Phase 7*
- [ ] ⭐ `X-Frame-Options: DENY` or CSP `frame-ancestors 'none'` (clickjacking protection) → *Phase 7*
- [ ] ⭐ `X-Content-Type-Options: nosniff` → *Phase 7*
- [ ] ⭐ `Referrer-Policy: strict-origin-when-cross-origin` → *Phase 7*
- [ ] ⭐ `Permissions-Policy` — disable unused browser features (camera, mic, geolocation) → *Phase 7*
- [ ] ⭐ Strict CORS policy — explicit allowlist of origins, never `Access-Control-Allow-Origin: *` with credentials → *Phase 7*

---

## 13. Rate Limiting & DDoS Protection

- [ ] ⭐ Global and per-endpoint rate limits (especially login, password reset, OTP verification) → *Phase 10*
- [ ] CAPTCHA or proof-of-work challenges on high-abuse endpoints
- [ ] Layer 3/4 DDoS protection via CDN/cloud provider (Cloudflare, AWS Shield)
- [ ] ⭐ Set request size limits (body size, header size, upload size) to prevent resource exhaustion → *Phase 4*
- [ ] Implement circuit breakers and graceful degradation for downstream service failures

---

## 14. Database Security

- [ ] ⭐ Database not directly reachable from the public internet — access only via app tier / VPN / bastion → *Done: Docker network isolation; Neon in Phase 7*
- [ ] ⭐ Least-privilege DB accounts per service (no shared "root" DB user across microservices) → *Phase 7 (production setup)*
- [ ] Enable audit logging for schema changes and privileged queries
- [ ] ⭐ Automated encrypted backups with tested restore procedures → *Phase 7 (Neon managed backups)*
- [ ] Disable default accounts/sample databases on managed DB services
- [ ] ⭐ Enforce connection encryption (SSL/TLS) between app and DB → *Phase 7 (Neon enforces SSL)*

---

## 15. Backup, Disaster Recovery & Business Continuity

- [ ] Automated, encrypted, geographically redundant backups
- [ ] Documented and **tested** Recovery Time Objective (RTO) / Recovery Point Objective (RPO)
- [ ] Run periodic disaster recovery drills (restore from backup in an isolated environment)
- [ ] Immutable/versioned backups to protect against ransomware (can't be overwritten/deleted by a compromised app account)

---

## 16. Compliance & Governance

- [ ] Identify applicable frameworks: GDPR, CCPA, SOC 2, HIPAA, PCI-DSS — map controls accordingly
- [ ] Maintain a data processing inventory (what data, where stored, who has access)
- [ ] Vendor/third-party risk assessment for any external service handling user data
- [ ] Privacy policy and terms of service reviewed by legal, kept current with actual data practices

---

## 17. Pre-Launch Security Testing

- [ ] Full vulnerability scan (Nessus, OpenVAS, or cloud-native scanner) against staging environment
- [ ] Third-party penetration test before public launch, and annually/after major changes thereafter
- [ ] ⭐ Dependency audit for known CVEs (`npm audit`, `pip-audit`, `cargo audit`, etc.) → *Phase 9*
- [ ] Fuzz-test critical input parsers
- [ ] Verify all of the above checklist items in staging under production-like load, not just locally

---

## 18. Incident Response

- [ ] Written incident response plan with defined roles and escalation paths
- [ ] Pre-drafted breach notification templates (legal/PR reviewed) for regulatory deadlines (e.g., GDPR's 72-hour rule)
- [ ] Runbooks for common scenarios: credential leak, DDoS, data exfiltration, ransomware
- [ ] Practice tabletop incident response exercises at least annually
- [ ] Maintain an out-of-band communication channel in case primary systems are compromised

---

## 19. Post-Deployment: Ongoing Hygiene

- [ ] Recurring (automated) dependency and container image scans, not just at release time
- [ ] Quarterly access review — remove stale accounts, unused API keys, over-privileged roles
- [ ] Annual third-party penetration test at minimum
- [ ] Continuous patch management SLA (e.g., critical CVEs patched within 48–72 hours)
- [ ] Chaos/game-day exercises to validate monitoring and incident response actually work

---

## Quick-Reference: The 10 Highest-Leverage Items

If you can only prioritize a handful right now, these close the most common real-world breach vectors first:

1. ⭐ Parameterized queries everywhere (kills SQLi) → **Done** (SQLAlchemy ORM)
2. ⭐ Secrets in a vault, never in code/env files committed to git → **Done** (gitignored .env files); vault for prod in Phase 7
3. MFA on all admin/privileged accounts
4. ⭐ TLS 1.2+/1.3 enforced + HSTS → Phase 7
5. WAF + rate limiting in front of the app → Phase 10
6. ⭐ Least-privilege IAM roles (app, DB, CI/CD all scoped down) → Phase 7
7. ⭐ Centralized logging + alerting on auth anomalies → Phase 10
8. ⭐ Automated dependency vulnerability scanning in CI → Phase 9
9. Encrypted, tested backups → Phase 7
10. A written, rehearsed incident response plan

---

*This checklist targets OWASP ASVS Level 2–3 rigor. For regulated industries (finance, healthcare), add framework-specific controls (PCI-DSS, HIPAA) on top of this baseline.*
