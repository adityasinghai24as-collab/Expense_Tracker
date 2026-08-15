---
name: expense-tracker-patterns
description: >
  Transferable architectural patterns, conventions, and best practices from the Expense Tracker
  monorepo. Use this skill when starting a new full-stack project (FastAPI + React + PostgreSQL +
  Docker) to apply proven patterns for authentication, RBAC, observability, CI/CD, multi-environment
  IaC, and documentation structure.
---

# Expense Tracker — Transferable Patterns & Best Practices

This skill captures the architectural patterns, development conventions, and operational practices
established in the Expense Tracker monorepo. Apply these patterns when bootstrapping similar
full-stack projects.

---

## 1. Monorepo Structure Pattern

Organize the project as a monorepo with clear boundaries between backend, frontend, infrastructure,
and documentation.

```
project-root/
├── PROJECT_STATE.md          ← Living project state (source of truth)
├── TODO.md                   ← Phased development roadmap with checklists
├── docker-compose.yml        ← Multi-service orchestration
├── .agents/CONTEXT.md        ← AI agent instructions
│
├── architecture-study/       ← Design documents (HLD, LLD, security)
├── backend/                  ← FastAPI application
│   ├── app/                  ← Application modules (models, schemas, routers, auth)
│   ├── tests/                ← Pytest test suite
│   ├── load_tests/           ← Locust load tests
│   └── config/               ← Requirements, env templates
├── frontend/                 ← React + Vite application
│   └── src/                  ← Components, pages, context, services
├── infrastructure/           ← Terraform IaC
│   └── environments/         ← Per-environment variable files
├── config/                   ← Observability configs (Loki, Promtail, Grafana)
└── docs/                     ← Operational guides and how-tos
```

**Key principle**: Each directory has a single responsibility. Backend code never leaks into
frontend. Infrastructure is fully decoupled from application code.

---

## 2. FastAPI Async Database Pattern

Use SQLAlchemy 2.0 async with `asyncpg` for non-blocking database operations.

### Engine & Session Factory (Singleton)
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,                # Disable in production for performance
    pool_pre_ping=True,        # Detect stale connections before queries
    pool_size=20,              # Tune for expected concurrency
    max_overflow=10,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,    # Prevent lazy re-fetch in async context
)
```

### Dependency Injection
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Environment Parity
Support both `DATABASE_URL` (Docker/production) and individual `DB_*` vars (local dev):
```python
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

---

## 3. JWT Authentication Pattern

Implement persistent login using short-lived access tokens + long-lived refresh tokens in HttpOnly cookies.

### Token Strategy
| Token | Lifetime | Storage | Purpose |
|-------|----------|---------|---------|
| Access Token | 15 min | React state (memory) | API authorization header |
| Refresh Token | 7-30 days | HttpOnly, Secure, SameSite cookie | Silent session renewal |

### Key Implementation Points
- **Never store tokens in localStorage** — XSS vulnerability
- **Rotate refresh tokens on every use** — issue a new token on each `/auth/refresh` call
- **Store refresh token hash in DB** — enables "logout everywhere" by clearing the column
- **Bcrypt cost ≥ 12** — OWASP recommendation
- **Password policy**: Minimum 12 chars, check against HaveIBeenPwned API (no arbitrary complexity rules)
- **Account lockout**: Track `failed_login_attempts` and `locked_until` for exponential backoff
- **OTP email verification**: Block disposable emails, require email verification before login

### Frontend Interceptor Pattern
```javascript
// Axios interceptor: on 401, silently refresh and retry
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401 && !error.config._retry) {
            error.config._retry = true;
            await refreshAccessToken();
            return api(error.config);
        }
        return Promise.reject(error);
    }
);
```

---

## 4. Dual-Layer Feature Gating Pattern (RBAC + LaunchDarkly)

Implement feature access control at two levels:

1. **Global Release Toggle** (LaunchDarkly) — "Is this feature turned on for production?"
2. **User Subscription Tier** (RBAC) — "Does this user's plan include this feature?"

### RBAC via Computed Property
```python
class User(Base):
    role = Column(String, default="free")  # free, pro, enterprise, admin

    @property
    def features_enabled(self):
        is_pro = self.role in ["pro", "enterprise", "admin"]
        is_enterprise = self.role in ["enterprise", "admin"]
        return {
            "enable_receipt_scanning": is_pro,
            "enable_autonomous_agent": is_enterprise,
        }
```

### Enforcement Dependency
```python
def require_feature(flag_name: str, user=None):
    # 1. Check LaunchDarkly global toggle (TODO)
    # 2. Check user subscription tier
    if user and not user.features_enabled.get(flag_name, False):
        raise HTTPException(403, "Upgrade your plan to access this feature.")
```

---

## 5. Docker Compose Development Stack Pattern

Orchestrate the full development environment with a single command.

### Service Architecture
```yaml
services:
  db:           # PostgreSQL 15-Alpine with health checks
  redis:        # Redis 7-Alpine for caching and rate limiting
  backend:      # FastAPI (depends_on: db + redis)
  loki:         # Log aggregation database
  promtail:     # Log collector (scrapes Docker container logs)
  grafana:      # Visualization dashboard (anonymous auth for local dev)
```

### Key Conventions
- **Named volumes** for data persistence (`expense-tracker-postgres-data`)
- **Bridge network** for inter-container DNS (`expense-tracker-network`)
- **Health checks** on critical services (db) with `service_healthy` dependency condition
- **JSON-file logging driver** with size limits on backend

---

## 6. Observability Stack Pattern (PLG)

Use Promtail → Loki → Grafana for centralized logging.

### Application Logging (structlog)
```python
import structlog

# Development: Pretty console output
# Production: JSON structured logs (parseable by Loki)
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # or ConsoleRenderer() for dev
    ]
)
```

### Error Tracking
Integrate Sentry for real-time error tracking on both backend and frontend:
```python
if sentry_dsn:
    sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=1.0)
```

---

## 7. Multi-Environment IaC Pattern (Terraform)

Use per-environment variable files with isolated remote state.

### Directory Structure
```
infrastructure/
├── main.tf           ← Resource definitions (parameterized by env)
├── variables.tf      ← Input variables + feature flags
├── providers.tf      ← Provider config with GCS remote backend
├── outputs.tf        ← URLs, flags
└── environments/
    ├── dev.tfvars
    ├── staging.tfvars
    └── prod.tfvars
```

### State Isolation
```bash
terraform init -backend-config="prefix=terraform/state/dev"
terraform plan -var-file=environments/dev.tfvars
```

---

## 8. CI/CD Pipeline Pattern (Jenkins)

Use a single declarative `Jenkinsfile` with branch → environment auto-detection.

| Branch | Environment | Approval |
|--------|-------------|----------|
| `develop` | dev | No |
| `staging` | staging | No |
| `main` | prod | **Yes** (manual gate) |

### Pipeline Stages
1. Resolve Environment (from branch)
2. Code Quality (Ruff + ESLint + SonarQube)
3. Security Scans (Trivy)
4. Unit Tests (Pytest + Vitest)
5. Build & Push (Docker → Artifact Registry)
6. Production Approval (manual gate, main only)
7. Deploy Infrastructure (Terraform apply)
8. Smoke Test (health check verification)

---

## 9. Testing Strategy

### Backend (Pytest)
- Use `pytest-asyncio` + `httpx.AsyncClient` for async endpoint testing
- **Transaction rollback fixtures**: Wrap every test in a nested transaction, rollback after completion
- Mock external side-effects (`BackgroundTasks`, email sending) with `unittest.mock.patch`

### Load Testing (Locust)
- Simulate 500-1000 concurrent users performing typical workflows
- Target: p95 response times under 200ms
- Tune SQLAlchemy `pool_size` and `max_overflow` based on results

---

## 10. Documentation Strategy — Cross-Linked Graph

All documentation files should form a navigable graph with bidirectional links.

### Conventions
- **Standard relative markdown links** (`[text](../path/to/file.md)`) — compatible with GitHub, VS Code, and Obsidian
- **See Also footer** on every doc file — lists related documentation and key code files
- **Inline code links** where tasks reference specific files — e.g., `[models.py](backend/app/models.py)`
- **Documentation Index table** in PROJECT_STATE.md listing all docs with brief descriptions
- **Related Documentation table** in TODO.md at the top for quick navigation

### Security Headers Middleware
```python
class SecurityHeadersMiddleware:
    async def __call__(self, scope, receive, send):
        headers.append("X-Content-Type-Options", "nosniff")
        headers.append("X-Frame-Options", "DENY")
        headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
        headers.append("Content-Security-Policy", "default-src 'self'; ...")
```

---

## 11. Security Conventions

- **Target**: OWASP ASVS Level 2 compliance
- **CORS**: Strict allowlist in production (never `*` with credentials)
- **Cookies**: `HttpOnly`, `Secure`, `SameSite=Lax`
- **Rate limiting**: Per-IP and per-user, stricter on auth endpoints
- **Input validation**: Pydantic schemas at the API boundary, server-side only (client-side is UX)
- **Secrets**: Never in source control. Use env vars or secrets manager. Enforce with pre-commit hooks (gitleaks).
- **Error handling**: Generic messages externally, detailed logs internally. Global exception handler in FastAPI.
