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

### Current Models (Placeholders)

```
expense-tracker/
└── backend/
    └── app/
        └── models.py
```

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    features_enabled JSON,
    refresh_token VARCHAR,
    token_expires_at TIMESTAMP,
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
- `features_enabled`: JSON object for feature flags (e.g., {"ai_receipt_scan": true})
- `hashed_password`: Bcrypt-hashed password (never store plaintext)
- `refresh_token`: Current valid refresh token hash (nullable — null means logged out)
- `token_expires_at`: When the refresh token expires
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp
- **Relationship**: One-to-Many with Expenses (cascade delete)

#### Expenses Table
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    amount FLOAT NOT NULL,
    description TEXT,
    category VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
```

**Fields**:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `amount`: Expense amount (required)
- `description`: Expense description (optional)
- `category`: Expense category (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp
- **Relationship**: Many-to-One with Users

### ORM Classes Location
- **File**: `backend/app/models.py`
- **Base Class**: `database.Base` (SQLAlchemy declarative base)
- **Type**: Async-compatible SQLAlchemy ORM models

### Validation Schemas Location
- **File**: `backend/app/schemas.py`
- **Schemas**: UserCreate, UserResponse, ExpenseCreate, ExpenseResponse, ExpenseUpdate
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

#### Docker & DevOps
- ✓ Docker Compose orchestration (db + backend)
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

### 🔨 In Progress / Next Steps (Priority Order)

#### 1. **Add Feature Flagging System** (High Priority)
   - Add `features_enabled` JSON column to User model
   - Create Admin API endpoint `PUT /admin/users/{id}/features`
   - Implement frontend FeatureFlagProvider context
   - Note: Required before rolling out AI features to users.

#### 2. **Add Authentication with Persistent Login** (High Priority)
   - Implement JWT token-based auth (access token + refresh token)
   - Add password hashing (bcrypt via passlib)
   - Create auth endpoints: register, login, refresh, logout, me
   - Store refresh token in HttpOnly cookie for persistent login
   - Store refresh token hash in DB for server-side revocation
   - Add `get_current_user` dependency for protected routes
   - Frontend: AuthContext with silent token refresh on app load
   - **Files to create**: `backend/app/auth.py`, `frontend/src/context/AuthContext.jsx`
   - **Files to modify**: `backend/app/models.py`, `backend/app/schemas.py`

#### 2. **Implement Expense CRUD Operations** (High Priority)
   - GET `/expenses` - List user expenses (with pagination)
   - POST `/expenses` - Create expense
   - GET `/expenses/{id}` - Get specific expense
   - PUT `/expenses/{id}` - Update expense
   - DELETE `/expenses/{id}` - Delete expense
   - **Files to modify**: `backend/main.py`

#### 3. **Add Category Management** (Medium Priority)
   - Create Category model in models.py
   - Endpoints for CRUD operations on categories
   - Link categories to expenses

#### 4. **Frontend Features** (Medium Priority)
   - Dashboard with expense statistics
   - Expense form (create/edit)
   - Expense list with filtering/sorting
   - Category management UI
   - User profile page

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

- Database models are placeholders (User, Expense) - need expansion
- No authentication system implemented (Phase 3 — Tasks 10-16)
- Persistent login requires HttpOnly cookie support (CORS must allow credentials)
- No API endpoints for actual expense operations
- No frontend pages (only connection status monitor)
- Frontend API proxy only works during `npm run dev` (need to configure for production)
- No database migrations set up (Alembic installed but not configured)
- No error handling middleware in FastAPI

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
├── backend service (builds ./backend/Dockerfile)
│   └── depends_on: db (health condition)
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
| `PROJECT_STATE.md` | This file — persistent memory |
| `README.md` | Main project README |
| `Jenkinsfile` | CI/CD Pipeline (multi-environment) |
| `sonar-project.properties` | SonarQube code quality config |
| `architecture-study/high-level-design.md` | System architecture and requirements |
| `architecture-study/security-checklist.md` | **OWASP ASVS / CIS / NIST security deployment checklist** |
| `docs/TERRAFORM_SETUP.md` | Terraform infrastructure guide |
| `docs/JENKINS_SETUP.md` | Jenkins CI/CD setup guide |
| `docs/DEPLOYMENT_CHECKLIST.md` | Per-environment deployment checklist & rollback |
| `docs/DOCKER_SETUP.md` | Full Docker guide |
| `docs/DOCKER_QUICK_REF.md` | Docker commands |
| `docs/DOCKER_ARCHITECTURE.txt` | Architecture overview |
| `docs/POSTGRES_SETUP.md` | PostgreSQL setup |
| `docs/DB_INTEGRATION.md` | Database integration |
| `docs/QUICK_REFERENCE.md` | General quick reference |

---

## 🎓 Last Updated

**Current Iteration**: Multi-Environment CI/CD + Terraform IaC + Feature Flags Complete
**Status**: Infrastructure fully automated. Ready for feature development (authentication with persistent login, expense CRUD)
**Next Session**: Start with Phase 3 — Authentication (Tasks 13-16)
