# Project Rules — Expense Tracker

## Context & Token Efficiency
- Always consult [`TODO.md`](../TODO.md), [`PROJECT_STATE.md`](../PROJECT_STATE.md), [`architecture-study/high-level-design.md`](../architecture-study/high-level-design.md) first for project context before reading source code files.
- Use the .md documentation as the primary source of truth for task descriptions, architecture decisions, and current progress.
- Only read source files when you need to see the actual implementation details or make edits.

# Copilot Instructions - Expense Tracker Monorepo

## 🎯 MANDATORY PRE-PROCESSING INSTRUCTION

**BEFORE responding to ANY user prompt or generating ANY code, you MUST:**

1. **Silently read and internalize** [`PROJECT_STATE.md`](../PROJECT_STATE.md) from the repository root
2. **Verify the current state** of:
   - Tech stack versions
   - Database schema and models
   - Environment variables and connection strings
   - Completed features vs. pending work
   - File structure and organization
3. **Update your context** with the latest status from PROJECT_STATE.md
4. **Never** make assumptions about what's implemented or what's pending

---

## 📋 Context Summary (Quick Reference)

This monorepo is a **full-stack Expense Tracker** targeting **Google Cloud Run** deployment:

### Architecture
- **Backend**: FastAPI + SQLAlchemy async ORM + PostgreSQL 15
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Containerization**: Docker Compose (development), Dockerfile (production)
- **Deployment**: Docker containers (local) → Google Cloud Run (production)

### Tech Stack
```
Backend:  FastAPI 0.109.0 | SQLAlchemy 2.0.23 | asyncpg 0.29.0 | PostgreSQL 15-Alpine
Frontend: React 18.2.0 | Vite 5.0.8 | Tailwind CSS 3.4.1
DevOps:   Docker Compose 3.9 | Python 3.11-slim | Node 18+
```

### 📚 Documentation Map

| Category | Documents |
|---|---|
| **Project State** | [`PROJECT_STATE.md`](../PROJECT_STATE.md) · [`TODO.md`](../TODO.md) |
| **Architecture** | [`high-level-design.md`](../architecture-study/high-level-design.md) · [`low-level-design.md`](../architecture-study/low-level-design.md) · [`security-checklist.md`](../architecture-study/security-checklist.md) |
| **User-Facing** | [`USER_GUIDE.md`](../docs/USER_GUIDE.md) |
| **DevOps** | [`TERRAFORM_SETUP.md`](../docs/TERRAFORM_SETUP.md) · [`JENKINS_SETUP.md`](../docs/JENKINS_SETUP.md) · [`DEPLOYMENT_CHECKLIST.md`](../docs/DEPLOYMENT_CHECKLIST.md) |
| **Features** | [`RBAC.md`](../docs/RBAC.md) · [`launchdarkly-integration-guide.md`](../docs/launchdarkly-integration-guide.md) · [`AGENTIC_AI_SETUP.md`](../docs/AGENTIC_AI_SETUP.md) |
| **Quality** | [`TESTING_GUIDE.md`](../docs/TESTING_GUIDE.md) · [`OBSERVABILITY_GUIDE.md`](../docs/OBSERVABILITY_GUIDE.md) |

### Key Source Files

| File | Purpose |
|------|---------|
| [`PROJECT_STATE.md`](../PROJECT_STATE.md) | **THE SOURCE OF TRUTH** for current state |
| [`TODO.md`](../TODO.md) | Phase-by-phase development roadmap |
| [`docker-compose.yml`](../docker-compose.yml) | Multi-service orchestration (db + backend + redis + PLG stack) |
| [`backend/main.py`](../backend/main.py) | FastAPI application entry point (routes, middleware, startup) |
| [`backend/app/database.py`](../backend/app/database.py) | Async connection pool, engine, session factory, health checks |
| [`backend/app/models.py`](../backend/app/models.py) | SQLAlchemy ORM models (User, Expense, Category) |
| [`backend/app/schemas.py`](../backend/app/schemas.py) | Pydantic validation schemas |
| [`backend/app/auth.py`](../backend/app/auth.py) | JWT auth, password hashing, token management |
| [`backend/app/feature_flags.py`](../backend/app/feature_flags.py) | RBAC enforcement (deprecated for global flags — LaunchDarkly pending) |
| [`backend/app/logger.py`](../backend/app/logger.py) | Structured logging via structlog |
| [`backend/app/rate_limiter.py`](../backend/app/rate_limiter.py) | Rate limiter (implemented, not yet wired) |
| [`backend/app/exceptions.py`](../backend/app/exceptions.py) | Global exception handlers |
| [`backend/app/routers/auth_routes.py`](../backend/app/routers/auth_routes.py) | Auth endpoints (register, login, OTP, refresh, logout) |
| [`backend/app/routers/user_routes.py`](../backend/app/routers/user_routes.py) | User management endpoints |
| [`backend/app/routers/expense_routes.py`](../backend/app/routers/expense_routes.py) | Expense CRUD endpoints |
| [`backend/app/routers/category_routes.py`](../backend/app/routers/category_routes.py) | Category CRUD endpoints |
| [`frontend/src/App.jsx`](../frontend/src/App.jsx) | React root component |
| [`frontend/src/context/AuthContext.jsx`](../frontend/src/context/AuthContext.jsx) | Auth state, token refresh, useAuth hook |
| [`frontend/src/context/FeatureFlagContext.jsx`](../frontend/src/context/FeatureFlagContext.jsx) | Feature flag context and useFeatureFlag hook |
| [`frontend/src/services/api.js`](../frontend/src/services/api.js) | Centralized API service layer |
| [`Jenkinsfile`](../Jenkinsfile) | CI/CD pipeline (placeholder, Phase 9) |
| [`infrastructure/`](../infrastructure/) | Terraform IaC (providers, variables, main, outputs) |

---

## 🔄 Workflow Rules

### When Starting a New Session
1. Read [`PROJECT_STATE.md`](../PROJECT_STATE.md) completely
2. Note the "Current Status" section carefully
3. Identify what's ✅ complete vs. 🔨 in progress vs. ⏳ pending
4. Check the "Next Steps (Priority Order)" section

### When Making Code Changes
1. **Verify file locations** - Use the file structure from [`PROJECT_STATE.md`](../PROJECT_STATE.md)
2. **Update models/schemas** - All must be in `backend/app/` directory
3. **Check imports** - Backend uses `from app.database import ...`
4. **Environment variables** - Support both `DATABASE_URL` and individual `DB_*` vars
5. **Docker-aware** - Test assumptions with Docker Compose

### When Implementing Features
1. **Add to [`models.py`](../backend/app/models.py)** first (SQLAlchemy ORM)
2. **Add schema validation** in [`schemas.py`](../backend/app/schemas.py) (Pydantic)
3. **Add routes** in [`backend/app/routers/`](../backend/app/routers/) using `APIRouter`
4. **Update documentation** in [`PROJECT_STATE.md`](../PROJECT_STATE.md) when complete
5. **Test locally** with `docker compose up -d`

### When Creating New Files
- **Python**: Place in `backend/app/` (if module) or `backend/` (if script)
- **Documentation**: Place in `docs/` with descriptive name. **Add cross-links** to related docs using relative markdown links.
- **Config**: Place in `backend/config/`
- **Scripts**: Place in `backend/scripts/`

---

## 🗂️ Critical Project Paths

```
expense-tracker/
├── PROJECT_STATE.md              ← READ THIS FIRST
├── TODO.md                       ← Development roadmap
├── docker-compose.yml            ← Multi-service orchestration
├── Jenkinsfile                   ← CI/CD pipeline (placeholder)
├── sonar-project.properties      ← SonarQube config
├── .agents/
│   └── CONTEXT.md                ← YOU ARE HERE
│
├── architecture-study/
│   ├── high-level-design.md      ← System architecture & requirements
│   ├── low-level-design.md       ← Design patterns, DB schema, API spec
│   └── security-checklist.md     ← OWASP ASVS security checklist
│
├── backend/
│   ├── Dockerfile                ← Multi-stage build
│   ├── main.py                   ← FastAPI app + SecurityHeadersMiddleware
│   ├── app/
│   │   ├── database.py           ← Async connection pool
│   │   ├── models.py             ← SQLAlchemy models (User, Expense, Category)
│   │   ├── schemas.py            ← Pydantic schemas
│   │   ├── auth.py               ← JWT auth, bcrypt, token management
│   │   ├── feature_flags.py      ← RBAC enforcement (LaunchDarkly pending)
│   │   ├── logger.py             ← structlog structured logging
│   │   ├── rate_limiter.py       ← Rate limiter (not yet wired)
│   │   ├── email_utils.py        ← Email/OTP sending
│   │   ├── exceptions.py         ← Global exception handlers
│   │   └── routers/
│   │       ├── auth_routes.py    ← Register, login, OTP, refresh, logout
│   │       ├── user_routes.py    ← User management
│   │       ├── expense_routes.py ← Expense CRUD
│   │       └── category_routes.py← Category CRUD
│   ├── tests/
│   │   ├── conftest.py           ← Test fixtures (transaction rollback)
│   │   ├── test_auth.py          ← Auth endpoint tests
│   │   └── test_health.py        ← Health endpoint tests
│   ├── load_tests/
│   │   └── locustfile.py         ← Locust load testing script
│   └── config/
│       └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── main.jsx              ← React entry point
│       ├── App.jsx               ← Root component + routing
│       ├── context/
│       │   ├── AuthContext.jsx    ← Auth state, token refresh, useAuth
│       │   ├── FeatureFlagContext.jsx ← Feature flag context
│       │   └── ToastContext.jsx   ← Toast notifications
│       ├── components/
│       │   ├── Navigation.jsx    ← Main nav bar
│       │   ├── Sidebar.jsx       ← Sidebar navigation
│       │   ├── MainLayout.jsx    ← Page layout wrapper
│       │   ├── ProtectedRoute.jsx← Auth route guard
│       │   ├── OtpInput.jsx      ← 6-digit OTP component
│       │   └── CategoryManager.jsx ← Category CRUD UI
│       ├── pages/
│       │   ├── Dashboard.jsx     ← Main dashboard
│       │   ├── AddExpense.jsx    ← Add expense form
│       │   ├── EditExpense.jsx   ← Edit expense form
│       │   ├── ExpenseList.jsx   ← Expense listing with filters
│       │   ├── Login.jsx         ← Login page
│       │   ├── Register.jsx      ← Registration + OTP verification
│       │   ├── Profile.jsx       ← User profile
│       │   └── Settings.jsx      ← User settings
│       └── services/
│           ├── api.js            ← Centralized API calls
│           └── categoryDetector.js ← Client-side category suggestion
│
├── infrastructure/
│   ├── main.tf                   ← Terraform resource definitions
│   ├── variables.tf              ← Input variables + feature flags
│   ├── providers.tf              ← Provider config (GCS backend)
│   ├── outputs.tf                ← Terraform outputs
│   └── environments/
│       ├── dev.tfvars
│       ├── staging.tfvars
│       └── prod.tfvars
│
├── config/
│   ├── loki-config.yaml          ← Loki log aggregation config
│   ├── promtail-config.yaml      ← Promtail log scraping config
│   └── grafana-datasources.yml   ← Grafana data source provisioning
│
└── docs/
    ├── USER_GUIDE.md             ← End-user feature overview
    ├── TESTING_GUIDE.md          ← Pytest + Locust testing guide
    ├── OBSERVABILITY_GUIDE.md    ← PLG logging stack guide
    ├── AGENTIC_AI_SETUP.md       ← Multi-agent AI setup
    ├── RBAC.md                   ← Role-Based Access Control
    ├── launchdarkly-integration-guide.md ← LaunchDarkly SDK guide
    ├── FEATURE_FLAGS_AND_RBAC.md ← ⚠️ DEPRECATED
    ├── TERRAFORM_SETUP.md        ← IaC deployment guide
    ├── JENKINS_SETUP.md          ← CI/CD pipeline guide
    └── DEPLOYMENT_CHECKLIST.md   ← Per-env deploy checklist
```

---

## 🔐 Database Configuration (Always Check [`PROJECT_STATE.md`](../PROJECT_STATE.md))

### Docker Compose Environment
```
DATABASE_URL=postgresql+asyncpg://admin:supersecret@db:5432/expensedb
DB_HOST=db (internal DNS)
```

### Local Development Environment
```
DATABASE_URL (if set) OR individual DB_* variables
DB_HOST=localhost (or from .env file)
```

### Connection Logic ([`backend/app/database.py`](../backend/app/database.py))
```python
if DATABASE_URL:
    # Use it (Docker/production)
else:
    # Construct from DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
```

---

## 📊 Current Database Schema (See [`PROJECT_STATE.md`](../PROJECT_STATE.md) for full details)

### Users Table
- `id` (PK), `email` (unique), `username` (unique), `full_name`, `hashed_password`, `is_active`, `is_verified`, `otp_code`, `otp_expires_at`, `role`, `refresh_token`, `token_expires_at`, `failed_login_attempts`, `locked_until`, `created_at`, `updated_at`
- `features_enabled`: Computed `@property` (not a DB column) — derives feature access from `role`
- Relationships: One-to-Many with Expenses and Categories (cascade delete)

### Categories Table
- `id` (PK), `name` (indexed), `color`, `icon`, `user_id` (FK, nullable — null = global), `created_at`, `updated_at`
- Relationships: Many-to-One with Users, One-to-Many with Expenses

### Expenses Table
- `id` (PK), `user_id` (FK), `category_id` (FK, nullable), `amount`, `description`, `created_at`, `updated_at`
- Relationship: Many-to-One with Users and Categories

---

## ✅ Completed Features (Don't Rebuild)

- [x] Backend folder structure (app/, config/, scripts/, docs/)
- [x] FastAPI application with CORS + SecurityHeadersMiddleware
- [x] SQLAlchemy async ORM connection pool
- [x] Health check endpoints (`/health`, `/health/db`)
- [x] Database models (User, Expense, Category) with Alembic migrations
- [x] Pydantic validation schemas (all CRUD + auth)
- [x] JWT authentication with HttpOnly refresh cookies + OTP email verification
- [x] Brute-force protection (exponential backoff + account lockout)
- [x] RBAC subscription tiers (free/pro/enterprise/admin)
- [x] User CRUD endpoints (admin-protected listing)
- [x] Expense CRUD endpoints (ownership-protected)
- [x] Category CRUD endpoints
- [x] Global exception handlers
- [x] Docker Compose orchestration (db + backend + redis + PLG stack)
- [x] Multi-stage Dockerfile, bridge network, persistent volume
- [x] Structured JSON logging (structlog) + Sentry integration
- [x] Grafana + Loki + Promtail observability stack
- [x] Frontend: React 18 + Vite + Tailwind CSS
- [x] Frontend: Auth context, feature flag context, toast notifications
- [x] Frontend: Login, Register (with OTP), Dashboard, AddExpense, EditExpense, ExpenseList, Profile, Settings pages
- [x] Frontend: Navigation, Sidebar, ProtectedRoute, CategoryManager components
- [x] Frontend: Centralized API service layer with token interceptor
- [x] Terraform IaC templates (multi-environment: dev/staging/prod)
- [x] Locust load testing setup
- [x] Cross-linked documentation graph

## 🔨 In-Progress / Next Steps

**Current Priority**:
1. LaunchDarkly Integration (Phase 12, Tasks 62-65) — See [`docs/launchdarkly-integration-guide.md`](../docs/launchdarkly-integration-guide.md)

**High Priority (SDE-3 Focus)**:
2. Multi-Currency Support (Phase 11, Task 54) — live FX API, Redis caching, cron jobs
3. Recurring Expenses system (Task 48) — background workers
4. Advanced Analytics & Async PDF Export (Task 49) — Celery/Redis queue
5. Budgets & Alerts (Task 50) — category limits with proactive notifications
6. Agentic AI Architecture (Tasks 57-61) — See [`docs/AGENTIC_AI_SETUP.md`](../docs/AGENTIC_AI_SETUP.md)

**Medium Priority**:
6. Expand Pytest test suite (Phase 8, Tasks 39-40) — See [`docs/TESTING_GUIDE.md`](../docs/TESTING_GUIDE.md)
7. Wire rate limiter into routes (Phase 10, Task 46)
8. Redis caching for analytics queries (Task 47)

**Lower Priority**:
9. Execute Terraform deployments (Phase 7, Task 36) — See [`docs/TERRAFORM_SETUP.md`](../docs/TERRAFORM_SETUP.md)
10. Jenkins CI/CD pipeline (Phase 9, Tasks 42-43) — See [`docs/JENKINS_SETUP.md`](../docs/JENKINS_SETUP.md)

---

## 🚀 Common Commands (Copy from [`PROJECT_STATE.md`](../PROJECT_STATE.md))

```bash
# Start all services
docker compose up -d

# Test API
curl http://localhost:8000/health/db

# View logs
docker compose logs -f backend

# Stop services
docker compose down
```

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **Forgetting to check [`PROJECT_STATE.md`](../PROJECT_STATE.md) first**
   - ✅ Always read it before responding

2. ❌ **Using wrong import paths** (e.g., `from database import` instead of `from app.database import`)
   - ✅ Check backend folder reorganization in [`PROJECT_STATE.md`](../PROJECT_STATE.md)

3. ❌ **Assuming features are implemented** that are only marked as "next steps"
   - ✅ Check the "Current Status" section

4. ❌ **Creating duplicate files or models**
   - ✅ Verify User, Expense, and Category models already exist in [`models.py`](../backend/app/models.py)

5. ❌ **Forgetting to consider Docker architecture**
   - ✅ Remember: backend container connects to `db` service, not `localhost`

6. ❌ **Not updating documentation when making changes**
   - ✅ Update [`PROJECT_STATE.md`](../PROJECT_STATE.md) when completing features
   - ✅ Add cross-links to related docs when creating new documentation

---

## 🎓 Self-Assessment Checklist

Before submitting code or making recommendations, ask yourself:

- [ ] Have I read [`PROJECT_STATE.md`](../PROJECT_STATE.md) completely?
- [ ] Do I understand the current tech stack and versions?
- [ ] Do I know which features are ✅ complete vs. 🔨 pending?
- [ ] Are my import paths correct for the reorganized backend structure?
- [ ] Is my code compatible with Docker Compose setup?
- [ ] Does my code follow the existing patterns (e.g., async/await)?
- [ ] Have I considered both Docker and local development environments?
- [ ] Should I update [`PROJECT_STATE.md`](../PROJECT_STATE.md) when I'm done?

---

## 📖 Learned Rules
- Always update documentation and markdown files when adding new features.
- Add cross-links to related docs when creating or modifying documentation files.
- Use standard relative markdown links for maximum compatibility (GitHub, VS Code, Obsidian).
