# PROJECT_STATE.md - Expense Tracker Monorepo

## 📋 Current Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Runtime**: Python 3.11 (Uvicorn ASGI server)
- **ORM**: SQLAlchemy 2.0.23 (async support)
- **Database Driver**: asyncpg 0.29.0 (async), psycopg2-binary 2.9.9 (sync/testing)
- **Validation**: Pydantic 2.6.1
- **Migrations**: Alembic 1.13.0
- **Env Management**: python-dotenv 1.0.0

### Database
- **Engine**: PostgreSQL 15-Alpine (Docker)
- **Development**: postgres:15-alpine container via docker-compose
- **Connection Pool**: SQLAlchemy AsyncSession with pool_pre_ping
- **Volume**: expense-tracker-postgres-data (named Docker volume)

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.8
- **Styling**: Tailwind CSS 3.4.1
- **CSS Processing**: PostCSS 8.4.32, Autoprefixer 10.4.16

### DevOps & Containerization
- **Orchestration**: Docker Compose 3.9
- **Backend Image**: Python 3.11-slim (multi-stage build)
- **Database Image**: postgres:15-alpine
- **Networking**: expense-tracker-network (bridge)
- **Target Deployment**: Google Cloud Run + Neon (DB) + Cloudflare Pages (Frontend)
- **CI/CD**: Jenkins Declarative Pipeline (multi-environment)
- **IaC**: Terraform with GCS remote state (per-environment isolation)
- **Code Quality**: SonarQube, Ruff, ESLint
- **Security Scanning**: Trivy
- **Feature Flags**: Environment-aware JSON config injected via Terraform

### Environments
| Environment | Branch | Cloud Run Suffix | Neon Branch |
|---|---|---|---|
| Development | `develop` | `-dev` | `dev` |
| Staging | `staging` | `-staging` | `staging` |
| Production | `main` | (none) | `main` |

---

## 🚀 Local Setup Commands

### Prerequisites
- Docker Desktop (includes Docker Compose)
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for frontend)
- PostgreSQL client tools (psql) - optional but recommended

### Full Stack (Docker - Recommended)

```bash
# Start all services (db + backend)
cd expense-tracker
docker compose up -d

# Verify services are running
docker compose ps

# Test API health
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/health/db

# View backend logs
docker compose logs -f backend

# Stop all services
docker compose down

# Stop and remove all data (clean slate)
docker compose down -v
```

### Backend Only (Local Development)

```bash
cd expense-tracker/backend

# Create .env file
python scripts/setup_db.py

# Edit .env with your PostgreSQL credentials
notepad .env  # Windows
nano .env     # macOS/Linux

# Install Python dependencies
pip install -r config/requirements.txt

# Test database connection
python scripts/test_db_connection.py

# Start FastAPI server
python main.py
# API at: http://localhost:8000/docs
```

### Frontend Only (Local Development)

```bash
cd expense-tracker/frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
# Frontend at: http://localhost:5173

# Build for production
npm run build

# Preview build
npm run preview
```

### macOS/Linux Automated Setup

```bash
cd expense-tracker/backend
bash scripts/setup_bash.sh
pip install -r config/requirements.txt
python main.py
```

---

## 🗄️ Database Schema

### Current Models

Defined in [`backend/app/models.py`](backend/app/models.py) using SQLAlchemy declarative base from [`backend/app/database.py`](backend/app/database.py).
Validation schemas in [`backend/app/schemas.py`](backend/app/schemas.py).

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    otp_code VARCHAR,
    otp_expires_at TIMESTAMP,
    role VARCHAR NOT NULL DEFAULT 'free',
    refresh_token VARCHAR,
    token_expires_at TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
```

**Fields**:
- `id`: Primary key
- `email`: Unique email address (indexed)
- `username`: Unique username (indexed)
- `full_name`: User's full name (optional)
- `is_active`: Account status
- `is_verified`: Whether the user has verified their email via OTP
- `otp_code`, `otp_expires_at`: One-time password for email verification
- `role`: RBAC subscription tier (`free`, `pro`, `enterprise`, `admin`). See [`docs/RBAC.md`](docs/RBAC.md)
- `features_enabled`: Computed `@property` (not a DB column) — derives feature access from `role`. See [`backend/app/models.py`](backend/app/models.py)
- `hashed_password`: Bcrypt-hashed password (never store plaintext). See [`backend/app/auth.py`](backend/app/auth.py)
- `refresh_token`: Current valid refresh token hash (nullable — null means logged out)
- `token_expires_at`: When the refresh token expires
- `failed_login_attempts`, `locked_until`: Brute-force protection (exponential backoff)
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp
- **Relationships**: One-to-Many with Expenses and Categories (cascade delete)

#### Categories Table
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    color VARCHAR,
    icon VARCHAR,
    user_id INT FOREIGN KEY REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
```

**Fields**:
- `id`: Primary key
- `name`: Category name (indexed)
- `color`, `icon`: Visual display properties (optional)
- `user_id`: Foreign key to users (nullable — null means a global/default category)
- **Relationships**: Many-to-One with Users, One-to-Many with Expenses

#### Expenses Table
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    category_id INT FOREIGN KEY REFERENCES categories(id),
    amount FLOAT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
```

**Fields**:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `category_id`: Foreign key to categories table (optional)
- `amount`: Expense amount (required)
- `description`: Expense description (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp
- **Relationship**: Many-to-One with Users, Many-to-One with Categories

### ORM Classes Location
- **File**: [`backend/app/models.py`](backend/app/models.py)
- **Base Class**: `database.Base` (SQLAlchemy declarative base)
- **Type**: Async-compatible SQLAlchemy ORM models

### Validation Schemas Location
- **File**: [`backend/app/schemas.py`](backend/app/schemas.py)
- **Schemas**: UserCreate, UserResponse, UserLogin, UserUpdate, ExpenseCreate, ExpenseResponse, ExpenseUpdate, CategoryCreate, CategoryResponse, TokenResponse, OTPVerifyRequest
- **Type**: Pydantic models for request/response validation

---

## 🔌 Environment Variables

### Docker Compose (Automatic)
Set in `docker-compose.yml` - no manual configuration needed:
```env
DATABASE_URL=postgresql+asyncpg://admin:supersecret@db:5432/expensedb
DB_USER=admin
DB_PASSWORD=supersecret
DB_HOST=db
DB_PORT=5432
DB_NAME=expensedb
```

### Local Development (.env file)
Located at: `backend/.env`

**Template** (`backend/config/.env.example`):
```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expense_tracker
```

### Database Connection Strings

**Docker/Production**:
```
postgresql+asyncpg://admin:supersecret@db:5432/expensedb
```

**Local Development**:
```
postgresql+asyncpg://postgres:postgres@localhost:5432/expense_tracker
```

### Backend Auto-Detection
- If `DATABASE_URL` is set → use it (Docker/production)
- Otherwise → construct from `DB_*` environment variables (local)

---

## 📊 Current Status

### ✅ Completed

#### Project Setup
- ✓ Monorepo folder structure organized (backend, frontend, docs)
- ✓ Frontend: Vite + React + Tailwind CSS
- ✓ Backend folder reorganization (app/, config/, scripts/, docs/)

#### Backend Development
- ✓ FastAPI application with CORS middleware
- ✓ SQLAlchemy async ORM with connection pool
- ✓ PostgreSQL async driver (asyncpg)
- ✓ Pydantic validation schemas
- ✓ Health check endpoints:
  - `GET /health` → API status
  - `GET /health/db` → Database connection status
- ✓ Environment variable management (dotenv)
- ✓ Database models (User, Expense - placeholders)

#### Database
- ✓ PostgreSQL 15-Alpine Docker image
- ✓ Named volume (expense-tracker-postgres-data) for persistence
- ✓ Health checks on database container
- ✓ Credentials configured (admin/supersecret - dev only)
- ✓ Alembic asynchronous migrations configured

#### Docker & DevOps
- ✓ Docker Compose orchestration (db + backend + redis)
- [x] Integrate Loki logging stack for robust log management
- [x] Transition Feature Flags to Role-Based Access Control (RBAC)ail) configured
- ✓ Backend Dockerfile (multi-stage build for optimization)
- ✓ .dockerignore for clean builds
- ✓ Bridge network (expense-tracker-network) for container communication
- ✓ Service dependency management (backend waits for DB health)
- ✓ Named volume for persistent data

#### Documentation
- ✓ `docs/DOCKER_SETUP.md` - Comprehensive Docker guide
- ✓ `docs/DOCKER_QUICK_REF.md` - Quick command reference
- ✓ `docs/DOCKER_ARCHITECTURE.txt` - Architecture overview
- ✓ `docs/POSTGRES_SETUP.md` - PostgreSQL installation guide
- ✓ `docs/DB_INTEGRATION.md` - Database integration reference
- ✓ `docs/QUICK_REFERENCE.md` - General quick reference
- ✓ Backend setup scripts (setup_db.py, setup_bash.sh, test_db_connection.py)

#### Frontend
- ✓ React 18 with Vite
- ✓ Connection status monitor component (App.jsx)
- ✓ API proxy to backend (/api/* → localhost:8000)
- ✓ Tailwind CSS styling
- ✓ Custom `OtpInput` component (6-digit, auto-focus, paste support)

#### 1. **LaunchDarkly Integration** (Current Priority)
   - [ ] Backend: Install server SDK, initialize singleton, update `require_feature`.
   - [ ] Frontend: Install client SDK, wrap app in provider, hydrate context on login.
   - [ ] Testing: Setup `TestData` mock source for offline development.

#### 2. **Implement Enterprise Feature Expansion** (High Priority - SDE-3 Focus)
   - [ ] **Multi-Currency Support**: Live FX API integration, Redis caching, and cron jobs for daily rates.
   - [ ] Build `Recurring Expenses` system via background workers.
   - [ ] Build `Advanced Analytics` with async PDF export via Celery/Redis queue.
   - [ ] Implement `Budgets & Alerts` logic.

#### 2. **Build Agentic AI Architecture** (High Priority)
   - [ ] Implement the `Autonomous Financial Advisor` (LangGraph Multi-Agent).
   - [ ] Setup `Local RAG` for Financial Documents using ChromaDB.
   - [ ] Add `Human-in-the-Loop` safety checks.
   - [ ] Wire up `Self-Healing` tool execution.
   - [ ] Implement `Voice-to-Action` frontend integration.

#### 3. **Testing & QA** (Medium Priority)
   - Ensure the AI features have strict testing and graceful fallbacks.
   - Scale test the PostgreSQL instance under analytics load.

#### 5. **Testing** (Medium Priority)
   - Pytest test suite for backend (unit + integration)
   - Jest tests for frontend
   - API endpoint tests

#### 6. **Data Validation & Error Handling** (Medium Priority)
   - Custom exception handlers
   - Validation error messages
   - Rate limiting

#### 7. **Multi-Environment Deployment via Terraform + Jenkins** (Lower Priority)
   - Follow instructions in `docs/TERRAFORM_SETUP.md` and `docs/JENKINS_SETUP.md`
   - Configure `environments/dev.tfvars`, `staging.tfvars`, `prod.tfvars`
   - Jenkins auto-detects environment from branch (`develop`→dev, `staging`→staging, `main`→prod)
   - Production deploys require manual approval gate
   - Use `docs/DEPLOYMENT_CHECKLIST.md` for every deployment

### ⚠️ Known Limitations / Technical Debt

- CORS currently set to `allow_origins=["*"]` — must be restricted before production (with `allow_credentials=True` for HttpOnly cookies)
- Feature flags module ([`backend/app/feature_flags.py`](backend/app/feature_flags.py)) is deprecated pending LaunchDarkly migration (see [`docs/launchdarkly-integration-guide.md`](docs/launchdarkly-integration-guide.md))
- Rate limiter ([`backend/app/rate_limiter.py`](backend/app/rate_limiter.py)) is implemented but not yet wired into routes globally
- `GET /admin/feature-flags` endpoint not yet implemented
- Database credentials are hardcoded dev defaults (`admin/supersecret`) — must use secrets manager for production

---

## 🔗 Key Connections & Dependencies

### Backend Dependencies Flow
```
main.py (FastAPI app)
├── app/database.py (AsyncSession, engine, health checks)
├── app/models.py (SQLAlchemy ORM models)
├── app/schemas.py (Pydantic validation)
└── config/requirements.txt (Python packages)
```

### Docker Architecture
```
docker-compose.yml
├── db service (postgres:15-alpine)
│   └── Volume: postgres_data
├── redis service (redis:7-alpine)
├── loki service (grafana/loki)
├── promtail service (grafana/promtail)
├── grafana service (grafana/grafana)
├── backend service (builds ./backend/Dockerfile)
│   └── depends_on: db, redis
└── network: expense-tracker-network (bridge)
```

### Frontend Backend Communication
```
Frontend (localhost:5173)
└── Vite dev proxy (/api/*)
    └── Backend (localhost:8000)
        └── Database (localhost:5432 or db:5432 in Docker)
```

---

## 📁 File Structure Reference

```
expense-tracker/
├── docker-compose.yml           ← Multi-service orchestration
├── .gitignore                   ← Repository ignore rules
├── README.md                    ← Main documentation
├── PROJECT_STATE.md             ← This file (persistent memory)
│
├── backend/
│   ├── Dockerfile               ← Multi-stage build
│   ├── .dockerignore            ← Build context excludes
│   ├── main.py                  ← FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py          ← Async connection pool
│   │   ├── models.py            ← SQLAlchemy ORM models
│   │   ├── schemas.py           ← Pydantic validation
│   │   └── auth.py              ← [NEW] JWT auth, password hashing, token management
│   ├── config/
│   │   ├── requirements.txt     ← Python dependencies
│   │   ├── .env.example         ← Env template
│   │   └── wrangler.toml        ← Cloudflare Workers config
│   ├── scripts/
│   │   ├── setup_db.py          ← Windows setup wizard
│   │   ├── setup_bash.sh        ← macOS/Linux setup
│   │   └── test_db_connection.py ← Connection tester
│   ├── docs/
│   │   ├── POSTGRES_SETUP.md    ← PostgreSQL guide
│   │   ├── DB_INTEGRATION.md    ← DB integration reference
│   │   └── QUICK_REFERENCE.md   ← Quick commands
│   └── .gitignore               ← Backend specific ignores
│
├── frontend/
│   ├── package.json             ← Node dependencies
│   ├── vite.config.js           ← Vite configuration
│   ├── tailwind.config.js       ← Tailwind CSS config
│   ├── postcss.config.js        ← PostCSS config
│   ├── index.html               ← HTML entry point
│   └── src/
│       ├── main.jsx             ← React entry point
│       ├── App.jsx              ← Root component
│       ├── index.css            ← Global styles
│       ├── components/
│       │   └── OtpInput.jsx     ← [NEW] Custom OTP input UI
│       ├── context/
│       │   └── AuthContext.jsx   ← [NEW] Auth state, token refresh, useAuth hook
│       └── pages/
│           ├── Login.jsx         ← [NEW] Login page
│           └── Register.jsx     ← [NEW] Registration page
│
├── docs/
│   ├── TERRAFORM_SETUP.md       ← Infrastructure deployment guide
│   ├── JENKINS_SETUP.md         ← Jenkins CI/CD setup guide
│   ├── DEPLOYMENT_CHECKLIST.md  ← Per-environment deployment checklist
│   ├── DOCKER_SETUP.md          ← Full Docker guide
│   ├── DOCKER_QUICK_REF.md      ← Docker command reference
│   └── DOCKER_ARCHITECTURE.txt  ← Architecture overview
├── infrastructure/
│   ├── environments/
│   │   ├── dev.tfvars           ← Development environment config
│   │   ├── staging.tfvars       ← Staging environment config
│   │   └── prod.tfvars          ← Production environment config
│   ├── providers.tf             ← Terraform provider config (GCS backend)
│   ├── variables.tf             ← Terraform input variables + feature flags
│   ├── main.tf                  ← Terraform resource definitions (env-scoped)
│   └── outputs.tf               ← Terraform outputs (URLs, flags)
```

---

## 🎯 Performance Notes

### Backend Optimizations
- Async/await for non-blocking database operations
- Connection pooling with SQLAlchemy (pre-ping health checks)
- Multi-stage Docker build (~280 MB final image)
- Minimal python:3.11-slim base image

### Frontend Optimizations
- Vite for instant server start & HMR
- Tailwind CSS utility-first (minimal CSS output)
- React 18 with modern hooks

### Database Optimizations
- postgres:15-alpine (lightweight)
- Indexed columns (email, username)
- Foreign key relationships with cascade delete

---

## 🔐 Security Reminders

⚠️ **Local Development Only**:
- Database credentials: admin/supersecret
- CORS: Allow-all (*/*)
- No authentication implemented yet

✅ **Before Production**:
- [ ] Change database password
- [ ] Implement authentication system (Phase 3 — persistent login with JWT + refresh tokens)
- [ ] Configure CORS properly (allow credentials for HttpOnly cookies)
- [ ] Configure CORS properly
- [ ] Set secure environment variables
- [ ] Use HTTPS
- [ ] Add rate limiting
- [ ] Implement input validation

---

## 📞 Quick Help

### Common Commands

**Start Everything** (Docker):
```bash
cd expense-tracker && docker compose up -d
```

**Test Connection**:
```bash
curl http://localhost:8000/health/db
```

**View Logs**:
```bash
docker compose logs -f backend
```

**Access API Docs**:
```
http://localhost:8000/docs
```

**Stop Everything**:
```bash
docker compose down
```

### Troubleshooting
- Backend won't connect: `docker compose logs backend`
- Port already in use: Edit docker-compose.yml port mappings
- Database won't start: `docker compose logs db`
- Reset everything: `docker compose down -v`

---

## 📚 Documentation Index

| File | Purpose |
|------|---------|
| **Root** | |
| [`PROJECT_STATE.md`](PROJECT_STATE.md) | This file — persistent memory and source of truth |
| [`TODO.md`](TODO.md) | Phase-by-phase development roadmap with task checklists |
| [`Jenkinsfile`](Jenkinsfile) | CI/CD Pipeline definition (multi-environment) |
| [`sonar-project.properties`](sonar-project.properties) | SonarQube code quality config |
| [`docker-compose.yml`](docker-compose.yml) | Multi-service Docker orchestration |
| **Architecture Study** | |
| [`architecture-study/high-level-design.md`](architecture-study/high-level-design.md) | System architecture, requirements, and deployment overview |
| [`architecture-study/low-level-design.md`](architecture-study/low-level-design.md) | Design patterns, DB schema, API spec, component architecture |
| [`architecture-study/security-checklist.md`](architecture-study/security-checklist.md) | OWASP ASVS / CIS / NIST security deployment checklist |
| **Guides (docs/)** | |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | End-user feature overview and application flow |
| [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) | Pytest unit tests and Locust load testing guide |
| [`docs/OBSERVABILITY_GUIDE.md`](docs/OBSERVABILITY_GUIDE.md) | Grafana + Loki + Promtail logging stack guide |
| [`docs/AGENTIC_AI_SETUP.md`](docs/AGENTIC_AI_SETUP.md) | LangGraph multi-agent AI setup and implementation |
| [`docs/RBAC.md`](docs/RBAC.md) | Role-Based Access Control and subscription tiers |
| [`docs/launchdarkly-integration-guide.md`](docs/launchdarkly-integration-guide.md) | LaunchDarkly SDK integration for dynamic feature flags |
| [`docs/FEATURE_FLAGS_AND_RBAC.md`](docs/FEATURE_FLAGS_AND_RBAC.md) | ⚠️ DEPRECATED — redirects to LaunchDarkly guide |
| **DevOps Guides (docs/)** | |
| [`docs/TERRAFORM_SETUP.md`](docs/TERRAFORM_SETUP.md) | Terraform IaC guide for multi-environment deployment |
| [`docs/JENKINS_SETUP.md`](docs/JENKINS_SETUP.md) | Jenkins CI/CD pipeline setup guide |
| [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) | Per-environment deployment checklist & rollback |
| **Agent Config** | |
| [`.agents/CONTEXT.md`](.agents/CONTEXT.md) | AI agent instructions and project rules |

---

## 🎓 Last Updated

**Current Iteration**: Phase 11 (Enterprise & Agentic AI Expansion) + Phase 12 (LaunchDarkly).
**Status**: Core application (Auth, CRUD, UI, Docker, Observability) is fully built. We are now expanding into enterprise features and migrating feature flags to LaunchDarkly.
**Next Session**: Begin LaunchDarkly SDK integration (Phase 12, Tasks 62-65) and/or enterprise features in Phase 11 of [`TODO.md`](TODO.md).

---

## 🔗 See Also

- [`TODO.md`](TODO.md) — Full development roadmap
- [`architecture-study/high-level-design.md`](architecture-study/high-level-design.md) — System architecture
- [`architecture-study/low-level-design.md`](architecture-study/low-level-design.md) — Design patterns and API spec
- [`architecture-study/security-checklist.md`](architecture-study/security-checklist.md) — Security hardening guide
- [`.agents/CONTEXT.md`](.agents/CONTEXT.md) — AI agent rules and context
