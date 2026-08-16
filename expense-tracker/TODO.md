# 📋 Expense Tracker — SDE-2 Development Guide

> **Goal**: Work through each phase sequentially. Each phase builds on the last.
> Check off tasks as you complete them. By the end, you will have a production-deployed, tested, full-stack application with a CI/CD pipeline.
>
> **Security Standard**: This project targets **OWASP ASVS Level 2** compliance.
> See [`architecture-study/security-checklist.md`](architecture-study/security-checklist.md) for the full 10-category deployment hardening checklist.

---

## Legend

- `[ ]` — Not started
- `[/]` — In progress
- `[x]` — Complete

---

## 📚 Related Documentation

| Category | Documents |
|---|---|
| **Architecture** | [High-Level Design](architecture-study/high-level-design.md) · [Low-Level Design](architecture-study/low-level-design.md) · [Security Checklist](architecture-study/security-checklist.md) |
| **Project State** | [PROJECT_STATE.md](PROJECT_STATE.md) · [.agents/CONTEXT.md](.agents/CONTEXT.md) |
| **User-Facing** | [User Guide](docs/USER_GUIDE.md) |
| **DevOps** | [Terraform Setup](docs/TERRAFORM_SETUP.md) · [Jenkins Setup](docs/JENKINS_SETUP.md) · [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md) |
| **Features** | [RBAC](docs/RBAC.md) · [LaunchDarkly Guide](docs/launchdarkly-integration-guide.md) · [Agentic AI Setup](docs/AGENTIC_AI_SETUP.md) |
| **Quality** | [Testing Guide](docs/TESTING_GUIDE.md) · [Observability Guide](docs/OBSERVABILITY_GUIDE.md) |

---

## Phase 1: Backend — Get the API Server Running Locally

> **Objective**: Start the FastAPI backend on your machine and confirm the health endpoint responds.

### 1.1 Environment Setup
#### Task 1 — Environment Setup
- [x] Ensure you have Python 3.11+ installed (`python --version`)
- [x] Create and activate a virtual environment:
  ```bash
  # From the repo root
  python -m venv venv
  venv\Scripts\activate        # Windows
  # source venv/bin/activate   # macOS/Linux
  ```
- [x] Install backend dependencies:
  ```bash
  pip install -r expense-tracker/backend/config/requirements.txt
  ```

### 1.2 Run the Backend Server
#### Task 2 — Run the Backend Server
- [x] Navigate to `expense-tracker/backend/`
- [x] Start the FastAPI dev server:
  ```bash
  python main.py
  ```
- [x] Verify the API is alive by opening `http://localhost:8000/docs` in your browser
  - You should see the Swagger UI with the `/health` endpoint listed
- [x] Hit the health endpoint:
  ```bash
  curl http://localhost:8000/health
  ```
  - Expected response: `{"status": "ok", "message": "Expense Tracker API is running"}`

### 1.3 Understand the Backend Structure
#### Task 3 — Understand the Backend Structure
- [x] Read through `main.py` — understand how FastAPI initializes, adds CORS middleware, and registers routes
- [x] Read through `app/schemas.py` — understand how Pydantic models validate request/response data
- [x] Read through `app/models.py` — understand how SQLAlchemy ORM models map to database tables
- [x] Read through `app/database.py` — this is where most of your upcoming work will happen

> **🧠 Architect's Note**: Notice how [`main.py`](backend/main.py) imports from `app.database` but never touches raw SQL. This is the *Dependency Inversion Principle* in action — your API layer depends on abstractions (`get_db`), not concrete database details. This separation is what makes the backend testable, swappable, and scalable.

### ✅ Phase 1 Checkpoint
- [x] `http://localhost:8000/health` returns `{"status": "ok", ...}`
- [x] You can articulate what each file in `backend/app/` is responsible for

---

## Phase 2: Database — Connect PostgreSQL

> **Objective**: Stand up a PostgreSQL instance via Docker, then implement the database connection layer in `app/database.py`.

### 2.1 Start the Database with Docker
#### Task 4 — Start the Database with Docker
- [x] Make sure Docker Desktop is installed and running
- [x] From `expense-tracker/`, start only the database service:
  ```bash
  docker compose up db -d
  ```
- [x] Verify it's healthy:
  ```bash
  docker compose ps
  ```
  - Look for `expense-tracker-postgres` with status `healthy`
- [x] (Optional) Connect with a client to prove it works:
  ```bash
  psql -h localhost -U admin -d expensedb
  # Password: supersecret
  ```

### 2.2 Create a `.env` File for Local Development
#### Task 5 — Create a `.env` File for Local Development
- [x] Create `backend/.env` with the following content:
  ```env
  DB_USER=admin
  DB_PASSWORD=supersecret
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=expensedb
  ```
- [x] Verify that `backend/.env` is in your `.gitignore` (it should be — **never commit credentials**)

### 2.3 Implement the Database Connection (Code Tasks)

Open [`backend/app/database.py`](backend/app/database.py). You will complete **Tasks 6-11** in order.

#### Task 6 — Database Configuration (URL Construction)
- [x] Read `DATABASE_URL` from env vars. If it exists, use it directly.
- [x] If not, read individual `DB_*` vars and construct the connection strings:
  ```
  SYNC_DATABASE_URL  = "postgresql://{user}:{password}@{host}:{port}/{name}"
  ASYNC_DATABASE_URL = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
  ```

> **🧠 Architect's Note**: We support two modes because Docker Compose injects a full `DATABASE_URL`, but local development uses individual vars from a `.env` file. Supporting both means zero config changes between environments. This is called *environment parity* — a key principle from the [Twelve-Factor App](https://12factor.net/).

#### Task 7 — Create the Async Engine and Session Factory
- [x] Use `create_async_engine(ASYNC_DATABASE_URL, ...)` to create `async_engine`
- [x] Use `sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)` to create `AsyncSessionLocal`

> **🧠 Architect's Note**: `expire_on_commit=False` prevents SQLAlchemy from lazily re-fetching data after a commit, which would fail in an async context. This is a common gotcha. The `pool_pre_ping=True` option ensures stale connections are detected before queries, preventing cryptic "connection closed" errors in production.

#### Task 8 — Implement `get_db()` (Dependency Injection)
- [x] Make it an `async` generator that yields an `AsyncSession`
- [x] Use `async with AsyncSessionLocal() as session:` and `try/finally` to ensure cleanup

> **🧠 Architect's Note**: FastAPI calls this function via its `Depends()` system. Every route that needs the database declares `db: AsyncSession = Depends(get_db)`. This means your route functions *never* create or manage sessions themselves. That's Inversion of Control — the framework manages the resource lifecycle, not your business logic.

#### Task 9 — Implement `check_db_connection()` (Async Health Check)
- [x] Use `asyncpg.connect(...)` to open a raw async connection
- [x] Execute `SELECT 1` to prove the connection works
- [x] Close the connection and return `(True, "Connected successfully")`
- [x] Wrap in `try/except` and return `(False, str(error))` on failure

#### Task 10 — Implement `check_db_connection_sync()` (Sync Health Check)
- [x] Use `create_engine(SYNC_DATABASE_URL, poolclass=NullPool)` for a throwaway engine
- [x] Execute `text("SELECT 1")` inside `engine.connect()`
- [x] Dispose the engine and return the result tuple

#### Task 11 — Implement `init_db()` (Table Creation)
- [x] Use `async with async_engine.begin() as conn:` to get a connection
- [x] Run `await conn.run_sync(Base.metadata.create_all)` to create all tables

### 2.4 Verify End-to-End Database Connection
#### Task 12 — Verify End-to-End Database Connection
- [x] Start the backend again: `python main.py`
- [X] Watch the console — you should see: `✅ Database initialized and connected successfully`
- [X] Hit the database health endpoint:
  ```bash
  curl http://localhost:8000/health/db
  ```
  - Expected: `{"status": "ok", "message": "Connected successfully", "database": "postgresql"}`

### ✅ Phase 2 Checkpoint
- [X] PostgreSQL container is running and healthy
- [X] `http://localhost:8000/health/db` returns `"status": "ok"`
- [x] You can explain the difference between `asyncpg` (raw driver) and `SQLAlchemy` (ORM)

---

## Phase 3: Authentication — Persistent Login

> **Objective**: Implement a complete JWT-based authentication system with persistent login via refresh tokens. Users should stay logged in across browser sessions.

### 3.1 Install Auth Dependencies
#### Task 13 — Install Auth Dependencies
- [x] Add to `backend/config/requirements.txt`:
  ```
  python-jose[cryptography]==3.3.0
  passlib[bcrypt]==1.7.4
  ```
- [x] Run `pip install -r backend/config/requirements.txt`

### 3.2 Add Password Field to User Model

#### Task 14 — Update User Model for Auth
- [x] Open [`backend/app/models.py`](backend/app/models.py)
- [x] Add `hashed_password` column (String, nullable=False) to the User model
- [x] Add `refresh_token` column (String, nullable=True) — stores the current valid refresh token
- [x] Add `token_expires_at` column (DateTime, nullable=True) — when the refresh token expires

> **🧠 Architect's Note**: Storing the refresh token hash in the DB lets you implement "logout everywhere" — just clear the column and all existing refresh tokens become invalid. This is how Google/GitHub handle session revocation.

### 3.3 Create Auth Schemas

#### Task 15 — Auth Request/Response Schemas
- [x] Open [`backend/app/schemas.py`](backend/app/schemas.py)
- [x] Add `UserLogin` schema (username or email, password)
- [x] Add `TokenResponse` schema (access_token, refresh_token, token_type)
- [x] Add `TokenRefreshRequest` schema (refresh_token)
- [x] Update `UserCreate` to include a `password` field (plain text input, will be hashed before storage)

### 3.4 Implement the Auth Module

#### Task 16 — Create `backend/app/auth.py`
- [x] Create a new file [`backend/app/auth.py`](backend/app/auth.py)
- [x] Implement `hash_password(password: str) -> str` using passlib/bcrypt
- [x] Implement `verify_password(plain: str, hashed: str) -> bool`
- [x] Implement `create_access_token(data: dict) -> str` — short-lived JWT (15-30 min)
- [x] Implement `create_refresh_token(data: dict) -> str` — long-lived JWT (7-30 days)
- [x] Implement `decode_token(token: str) -> dict` — verifies and decodes a JWT
- [x] Read `SECRET_KEY` and `ALGORITHM` from env vars
- [x] Use bcrypt with cost factor ≥ 12 (OWASP recommendation; Argon2id preferred if passlib supports it)
- [x] Enforce strong password policy: min 12 chars, check against HaveIBeenPwned Pwned Passwords API (**not** arbitrary complexity rules like "must include uppercase + symbol")

> **🛡️ Security Ref**: See [`security-checklist.md`](architecture-study/security-checklist.md) Category 1 (Authentication & Authorization) for the full requirements.

> **🧠 Architect's Note**: Access tokens are short-lived (15 min) and sent with every API request. Refresh tokens are long-lived (7+ days) and stored in an HttpOnly cookie — this is what makes login "persistent". The browser automatically sends the cookie, so the user never has to re-enter credentials unless the refresh token expires or is revoked.

#### Task 17 — Create Auth Middleware / Dependency
- [x] Implement `get_current_user(token: str = Depends(oauth2_scheme))` dependency
- [x] This should decode the access token, look up the user in the DB, and return the User object
- [x] Return 401 if the token is expired or invalid

#### Task 18 — Create Auth Endpoints
- [x] `POST /auth/register` — Create a new user, block disposable emails, generate OTP, and send verification email
- [x] `POST /auth/verify-otp` — Verify OTP and return access + refresh tokens
- [x] `POST /auth/login` — Verify credentials and `is_verified` status, return access + refresh tokens
  - Set refresh token in an HttpOnly, Secure, SameSite cookie
  - Also store the refresh token hash in the user's DB row
- [x] `POST /auth/refresh` — Accept refresh token (from cookie), validate it against DB, return new access token
- [x] `POST /auth/logout` — Clear the refresh token from DB and delete the cookie
- [x] `GET /auth/me` — Return the current user's profile (protected route)
- [x] Implement account lockout / exponential backoff after 5 failed login attempts (security-checklist Category 2)
- [x] Set cookies with `HttpOnly`, `Secure`, `SameSite=Lax` flags (security-checklist Category 1)
- [x] Rotate refresh token on every use (issue new token on each `/auth/refresh` call)

### 3.5 Frontend Persistent Login

#### Task 19 — Auth Context and Token Management
- [x] Create [`frontend/src/context/AuthContext.jsx`](frontend/src/context/AuthContext.jsx)
- [x] Store access token in memory (React state) — NOT in localStorage (XSS risk)
- [x] On app load, call `POST /api/auth/refresh` to get a new access token from the HttpOnly cookie
  - If successful → user is "still logged in" (persistent login)
  - If failed → redirect to login page
- [x] Create `useAuth()` hook that provides: `user`, `login()`, `logout()`, `isAuthenticated`
- [x] Add an Axios/fetch interceptor that:
  - Attaches the access token to every request (`Authorization: Bearer <token>`)
  - On 401 response, automatically calls `/auth/refresh` and retries the request

#### Task 20 — Login and Register Pages
- [x] Create [`frontend/src/pages/Login.jsx`](frontend/src/pages/Login.jsx) — username or email + password form
- [x] Create [`frontend/src/pages/Register.jsx`](frontend/src/pages/Register.jsx) — email + password + username form, plus OTP verification step
- [x] Add routes for `/login` and `/register`
- [x] Redirect to dashboard after successful login
- [x] Add a `ProtectedRoute` wrapper component that redirects to `/login` if not authenticated

### 3.6 Verify Authentication End-to-End
#### Task 21 — Verify Authentication End-to-End
- [x] Register a new user via `POST /auth/register`
- [x] Login and confirm you receive tokens
- [x] Close the browser tab, reopen — confirm you are still logged in (refresh token cookie persists)
- [x] Hit a protected endpoint — confirm it works with the access token
- [x] Logout — confirm the refresh token is invalidated

### ✅ Phase 3 Checkpoint (Auth)
- [x] Users can register and login
- [x] Login persists across browser sessions (refresh token in HttpOnly cookie)
- [x] Protected routes reject unauthenticated requests with 401
- [x] Logout invalidates the session server-side
- [x] Passwords are hashed with bcrypt (cost ≥ 12); weak passwords are rejected
- [x] Failed login attempts trigger exponential backoff

---

## Phase 4: Backend — Build the CRUD API

> **Objective**: Implement the core REST endpoints for Users and Expenses. All expense endpoints should be protected (require authentication).

### 4.1 User Endpoints
#### Task 22 — User Endpoints
- [x] `GET /users` — List all users (admin only, return `list[UserResponse]`)
- [x] `GET /users/{user_id}` — Get a single user by ID
- [x] `PUT /admin/users/{user_id}/features` — Update user's feature flags (Admin only)

> **🧠 Architect's Note**: User creation is now handled by `POST /auth/register` (Phase 3). These endpoints are for user management, not registration.

> **🧠 Architect's Note**: Decide whether to keep routes in `main.py` or create a `backend/app/routers/` directory with separate files like `users.py` and `expenses.py`. The router approach scales better — it's how every production FastAPI app organizes its code. Use `APIRouter` and include it in `main.py` with `app.include_router(...)`.

### 4.2 Expense Endpoints (Protected)
#### Task 23 — Expense Endpoints
- [x] `POST /expenses` — Create a new expense (user_id derived from auth token)
- [x] `GET /expenses` — List current user's expenses (add query params for filtering by `category`)
- [x] `GET /expenses/{expense_id}` — Get a specific expense (must belong to current user)
- [x] `PUT /expenses/{expense_id}` — Update an expense (must belong to current user)
- [x] `DELETE /expenses/{expense_id}` — Delete an expense (must belong to current user)

### 4.3 Error Handling
#### Task 24 — Error Handling
- [x] Return `401` when authentication fails
- [x] Return `403` when user tries to access another user's data
- [x] Return `404` when a user or expense is not found
- [x] Return `422` for validation errors (Pydantic does this automatically)
- [x] Add a global exception handler for unexpected `500` errors

### 4.4 Category Endpoints
#### Task 25 — Category Endpoints
- [x] `POST /categories` — Create a custom category
- [x] `GET /categories` — List user's categories
- [x] `DELETE /categories/{id}` — Delete a category

### 4.5 Security Headers
#### Task 26 — Security Headers
- [x] Add SecurityHeadersMiddleware to FastAPI
- [x] Set X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Strict-Transport-Security, Content-Security-Policy

### 4.6 Verify with Swagger
#### Task 27 — Verify with Swagger
- [ ] Open `http://localhost:8000/docs`
- [ ] Authenticate via the "Authorize" button (use your login token)
- [ ] Test every endpoint through the interactive UI
- [ ] Create expenses for the logged-in user
- [ ] Confirm cascading delete works: delete a user → their expenses should vanish

### ✅ Phase 4 Checkpoint
- [ ] All CRUD endpoints respond correctly through Swagger
- [ ] Unauthenticated requests return 401
- [ ] Users can only access their own expenses
- [ ] Error cases return proper HTTP status codes
- [ ] Data persists across server restarts (because PostgreSQL is the backing store)

---

## Phase 5: Frontend — Build the UI

> **Objective**: Build a React frontend that communicates with your backend API.

### 5.1 Get the Frontend Running
#### Task 28 — Get the Frontend Running
- [ ] Navigate to `expense-tracker/frontend/`
- [ ] Install dependencies: `npm install`
- [ ] Start the dev server: `npm run dev`
- [ ] Open `http://localhost:5173` — you should see the existing shell page

### 5.2 Implement the Backend Health Check
#### Task 29 — Implement the Backend Health Check
- [ ] Open [`frontend/src/App.jsx`](frontend/src/App.jsx)
- [ ] Complete **Task 29**: implement the `fetch('/api/health')` call
- [ ] Handle the JSON response and update `isConnected` / `setError` state
- [ ] Uncomment the `setInterval` polling for live connection status
- [ ] Verify: the status indicator should turn **green** when the backend is running

> **🧠 Architect's Note**: Look at [`vite.config.js`](frontend/vite.config.js) — the `/api` proxy rewrites `/api/health` to `http://localhost:8000/health`. This means your frontend code never hardcodes the backend URL. In production, you'd replace this proxy with a real reverse proxy (like Nginx or Cloudflare) or use environment-based `VITE_API_URL` variables.

### 5.3 Setup Feature Flags Context
#### Task 30 — Setup Feature Flags Context
- [x] Create [`frontend/src/context/FeatureFlagContext.jsx`](frontend/src/context/FeatureFlagContext.jsx) to parse and provide the user's `features_enabled` globally.
- [x] Implement a `useFeatureFlag` hook to conditionally render UI elements (like AI buttons).

### 5.4 Build the Core Pages
#### Task 31 — Build the Core Pages
- [x] **Dashboard Page** — Show total expenses, expense breakdown by category, recent transactions
- [x] **Add Expense Page** — A form with amount, description, category fields. `POST` to `/api/expenses`
- [x] **Expense List Page** — Fetch and display all expenses from `GET /api/expenses`. Add filter/sort controls.
- [x] **User Profile Page** — Show user info from `GET /api/users/{id}`

### 5.5 Add Client-Side Routing
#### Task 32 — Add Client-Side Routing
- [x] Install React Router: `npm install react-router-dom`
- [x] Set up routes for Dashboard (`/`), Add Expense (`/add`), Expense List (`/expenses`), Profile (`/profile`)
- [x] Add a navigation bar component shared across all pages

### 5.6 Create a Reusable API Service Layer
#### Task 33 — Create a Reusable API Service Layer
- [x] Create [`frontend/src/services/api.js`](frontend/src/services/api.js)
- [x] Centralize all `fetch` calls (e.g., `getExpenses()`, `createExpense(data)`, `deleteExpense(id)`)
- [x] Handle errors consistently (toast notifications, error boundaries)

> **🧠 Architect's Note**: Never scatter `fetch()` calls across components. A service layer acts as a single point of change — if the API URL structure changes, you only update one file. This is the *Single Responsibility Principle* applied to data fetching.

### ✅ Phase 5 Checkpoint
- [ ] The health indicator turns green when the backend is running
- [ ] You can create an expense through the UI and see it appear in the list
- [ ] All pages navigate correctly via React Router
- [ ] API calls are centralized in a service file

---

## Phase 6: Docker — Run the Full Stack in Containers

> **Objective**: Run the backend, database, and frontend together using Docker Compose.

### 6.1 Verify Docker Compose Works for Backend + DB
#### Task 34 — Verify Docker Compose Works
- [ ] Stop any locally running backend/database processes
- [ ] Run: `docker compose up -d` (from `expense-tracker/`)
- [ ] Verify both services are up: `docker compose ps`
- [ ] Test: `curl http://localhost:8000/health/db`

### 6.2 Add Frontend to Docker Compose (Stretch)
#### Task 35 — Add Frontend to Docker Compose
- [ ] Create `frontend/Dockerfile` (use `node:18-alpine`, multi-stage build with Nginx)
- [ ] Add a `frontend` service to `docker-compose.yml`
- [ ] Configure Nginx to proxy `/api/*` requests to the backend container
- [ ] Verify the full stack runs with a single `docker compose up -d`

### ✅ Phase 6 Checkpoint
- [ ] `docker compose up -d` brings up all services
- [ ] The frontend can talk to the backend through Docker networking
- [ ] `docker compose down` cleanly stops everything

---

## Phase 7: Deployment — Ship to Production

> **Objective**: Deploy the backend, database, and frontend to Google Cloud Run.

### 7.1 Multi-Environment Deployment via Terraform
#### Task 36 — Terraform Deployment

> See [`docs/TERRAFORM_SETUP.md`](docs/TERRAFORM_SETUP.md) for step-by-step instructions.
- [x] Set up Infrastructure as Code (IaC) in `infrastructure/`
- [x] Create per-environment variable files (`environments/dev.tfvars`, `staging.tfvars`, `prod.tfvars`)
- [x] Configure GCS remote backend with per-environment state isolation
- [x] Parameterize all Terraform resource names by environment
- [ ] Create GCS bucket `expense-tracker-tf-state` in your GCP project
- [ ] Run `terraform plan -var-file=environments/dev.tfvars` to verify dev environment
- [ ] Run `terraform apply -var-file=environments/dev.tfvars` to deploy dev
- [ ] Deploy staging and production environments
- [ ] Verify `backend_url` and `frontend_url` outputs for each environment

### 7.2 Feature Flags
#### Task 37 — Backend Feature Flags

> See [`docs/launchdarkly-integration-guide.md`](docs/launchdarkly-integration-guide.md) for the LaunchDarkly migration plan and [`docs/RBAC.md`](docs/RBAC.md) for subscription tier details.
- [x] Create `backend/app/feature_flags.py` module
- [x] Define per-environment flag defaults in `environments/*.tfvars`
- [x] Inject `FEATURE_FLAGS` JSON env var into Cloud Run via Terraform
- [ ] Add `GET /admin/feature-flags` endpoint to `main.py`
- [ ] Gate experimental features (receipt scanning, smart categorization) behind flags

### 7.4 Production Hardening Checklist
#### Task 38 — Production Hardening
- [ ] Change database credentials from `admin/supersecret` to strong, unique values
- [ ] Restrict CORS `allow_origins` from `["*"]` to your actual frontend domain (with `allow_credentials=True`)
- [ ] Enable HTTPS (Google Cloud Run does this automatically)
- [ ] Add rate limiting to the backend
- [ ] Review and set proper `Content-Security-Policy` headers
- [ ] Add security response headers middleware to FastAPI:
  ```python
  # X-Content-Type-Options: nosniff
  # X-Frame-Options: DENY
  # Referrer-Policy: strict-origin-when-cross-origin
  # Permissions-Policy: camera=(), microphone=(), geolocation=()
  # Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  ```
- [ ] Use a dedicated secrets manager (not `.env` files) for production credentials
- [ ] Enforce TLS between app and DB (Neon enforces SSL by default)
- [ ] Ensure DB is not directly reachable from the public internet

> **🛡️ Security Ref**: See [`security-checklist.md`](architecture-study/security-checklist.md) Category 5 (Transport & Infrastructure Security) and Category 7 (Secrets & Config Management).

### ✅ Phase 7 Checkpoint
- [ ] Backend API is reachable on a public URL and connected to the production database
- [ ] Frontend is deployed and talking to the production backend
- [ ] Health check returns `"status": "ok"` on the live URL

---

## Phase 8: Testing — Add Automated Tests

> **Objective**: Write unit and integration tests to ensure code correctness and prevent regressions.

### 8.1 Backend Tests (pytest)
#### Task 39 — Backend Tests
- [x] Install test dependencies: `pip install pytest pytest-asyncio httpx`
- [x] Create `backend/tests/` directory with `__init__.py` and `conftest.py`
- [x] Write a test fixture that provides a test database session (use an in-memory SQLite or a separate test PostgreSQL DB)

> See [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) for testing setup, architecture, and conventions.
- [x] Write tests for:
  - [x] `GET /health` returns 200
  - [x] `POST /users` creates a user and returns 201
  - [x] `POST /expenses` creates an expense linked to a user
  - [x] `GET /expenses` returns the correct list
  - [x] `DELETE /users/{id}` cascades and deletes related expenses
  - [x] Invalid data returns 422

> **🧠 Architect's Note**: Test against the *API contract* (HTTP status codes, response shapes), not internal implementation. This lets you refactor internals freely without rewriting tests. Use `httpx.AsyncClient` with FastAPI's `TestClient` for async endpoint testing.

### 8.2 Frontend Tests (Vitest)
#### Task 40 — Frontend Tests
- [x] Install test dependencies: `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`
- [x] Configure Vitest in `vite.config.js`
- [x] Write tests for:
  - [x] API service functions mock `fetch` and return expected data
  - [x] Components render correctly with given props
  - [x] Form submission calls the correct API function

### 8.3 Load Testing (Locust / k6)
#### Task 41 — Load Testing
- [x] Install a load testing tool like Locust (`pip install locust`) or k6.
- [x] Create a `load_tests/` directory with a load testing script (e.g., `locustfile.py`).
- [ ] Write tests to simulate hundreds to thousands of concurrent users performing typical workflows (login, view dashboard, add expense).
- [ ] Measure and ensure 95th percentile response times are under 200ms during peak load.
- [ ] Identify any database bottlenecks or slow queries.

### ✅ Phase 8 Checkpoint
- [x] `pytest` passes all backend tests
- [x] `npx vitest run` passes all frontend tests
- [ ] Load tests verify stable performance under simulated traffic of 500-1000+ users
- [ ] You understand the difference between unit tests, integration tests, and end-to-end tests

---

## Phase 9: CI/CD — Automate Everything

> **Objective**: Set up a Jenkins CI/CD pipeline that tests, builds, and deploys on every push.
> See [`docs/JENKINS_SETUP.md`](docs/JENKINS_SETUP.md) for the full Jenkins + SonarQube server setup.
> See [`sonar-project.properties`](sonar-project.properties) for the SonarQube project config.

### 9.1 Create the CI Pipeline
#### Task 42 — CI Pipeline (Jenkinsfile)
- [/] Implement [`Jenkinsfile`](Jenkinsfile) with full declarative pipeline (11 stages):
  - **Stage 1**: Smoke Tests (`pytest -m smoke` — aborts pipeline on failure)
  - **Stage 2**: SAST & Linting (`ruff`, `bandit`, `pip-audit`, `eslint`, `npm audit`, Gitleaks)
  - **Stage 3**: Unit Tests (`pytest --cov` + `vitest --coverage`)
  - **Stage 4**: SonarQube Analysis (`sonar-scanner`)
  - **Stage 5**: SonarQube Quality Gate (`waitForQualityGate abortPipeline: true`)
  - **Stage 6**: Build & Push Docker images to Artifact Registry
  - **Stage 7**: Container Security Scan (`trivy image`)
  - **Stage 8**: Production Approval Gate (manual, `main` only)
  - **Stage 9**: Deploy Infrastructure (`terraform apply`)
  - **Stage 10**: Post-Deploy Smoke Test (curl `/health`, `/health/db`)
  - **Stage 11**: E2E Tests (`playwright test`, `staging` only)
- [ ] Configure Jenkins credentials (see `JENKINS_SETUP.md` Step 1).
- [ ] Create Multibranch Pipeline job in Jenkins pointing to this repo.
- [ ] Verify pipeline triggers on pushes to `develop`, `staging`, and `main`.

> **Security Ref**: See [`security-checklist.md`](architecture-study/security-checklist.md) § 9 (CI/CD Security).

### 9.2 SonarQube Quality Gate Configuration
#### Task 45 — SonarQube Server & Quality Gate Setup
- [ ] Start local SonarQube: `docker compose -f docker-compose.jenkins.yml up -d`.
- [ ] Log in to http://localhost:9000 (admin/admin), change the default password immediately.
- [ ] Create a new project → **Project Key**: `expense-tracker`.
- [ ] Generate a **Project Token** (My Account → Security → Generate Token).
- [ ] Add the token to Jenkins credentials as `sonar-token` (Secret Text).
- [ ] Configure the SonarQube server in Jenkins (Manage Jenkins → System → SonarQube servers):
  - **Name**: `SonarQubeServer` (must match `Jenkinsfile` exactly)
  - **URL**: `http://sonarqube:9000`
  - **Token**: select the `sonar-token` credential

#### Task 46 — Quality Gate Thresholds
- [ ] In SonarQube UI, navigate to **Quality Gates → Create** a custom gate named `Expense Tracker Gate`.
- [ ] Add the following conditions:
  - **Coverage on new code** ≥ 80%
  - **Duplicated Lines on new code** ≤ 3%
  - **Maintainability Rating on new code** = A
  - **Reliability Rating on new code** = A
  - **Security Rating on new code** = A
  - **Security Hotspots Reviewed** = 100%
- [ ] Assign this gate to the `expense-tracker` project.
- [ ] Run the pipeline once and verify the Quality Gate stage passes.

#### Task 47 — SonarQube Coverage Integration
- [ ] Confirm backend Pytest produces `backend/coverage.xml`: `pytest --cov=app --cov-report=xml:coverage.xml`.
- [ ] Confirm frontend Vitest produces `frontend/coverage/lcov.info`: `npx vitest run --coverage`.
- [ ] Verify both report paths match [`sonar-project.properties`](sonar-project.properties).
- [ ] View the SonarQube **Measures → Coverage** dashboard and confirm it reflects test results.

#### Task 48 — Branch Analysis & PR Decoration
- [ ] Enable **Automatic Analysis** or configure `sonar.branch.name` in the Jenkinsfile per branch.
- [ ] Install the **GitHub Pull Request Decoration** plugin in SonarQube.
- [ ] Configure a GitHub token in SonarQube so Quality Gate status appears inline on PRs.

### 9.3 Create the CD Pipeline (Multi-Environment)
#### Task 43 — CD Pipeline
- [/] Add **Build & Push** stage (Docker images → GCP Artifact Registry).
- [ ] Add **Deploy Infrastructure** stage (`terraform apply` with env-specific `.tfvars`).
- [ ] Add **Post-Deploy Smoke Test** stage (curl `/health`, `/health/db`).
- [/] Auto-detect environment from branch (`develop`→dev, `staging`→staging, `main`→prod).
- [/] Add **manual approval gate** before production deployments.
- [x] Created [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) with pre/post-deploy steps.

### 9.4 Branch Protection
#### Task 44 — Branch Protection
- [ ] Enable branch protection on `main` and `staging`.
- [ ] Require CI pipeline (including Quality Gate) to pass before merging PRs.
- [ ] Require at least 1 code review approval before merging.

### ✅ Phase 9 Checkpoint
- [ ] Every push triggers the full 11-stage pipeline automatically
- [ ] SonarQube Quality Gate blocks merges when code quality drops
- [ ] Coverage gate enforces ≥ 80% on new code
- [ ] Merging to `main` automatically deploys to production (with approval)
- [ ] Multi-environment deployments are fully automated via Terraform

---


## Phase 10: Enterprise Readiness (Advanced)

> **Objective**: Hardening the application for enterprise usage (observability, security, resilience).

### 10.1 Observability
#### Task 45 — Observability
- [x] Add structured JSON logging (e.g., using `structlog` in Python).
- [x] Integrate a monitoring/error tracking tool (e.g., Sentry) on both backend and frontend.
- [x] Local log aggregation and querying using Grafana + Loki + Promtail.

> See [`docs/OBSERVABILITY_GUIDE.md`](docs/OBSERVABILITY_GUIDE.md) for how to use the PLG logging stack.

### 10.2 Security & Rate Limiting
#### Task 46 — Rate Limiting
- [ ] Implement Rate Limiting on the backend API (e.g., using `slowapi` or Redis).
- [ ] Setup Audit Logging for critical actions (e.g., changing passwords or permissions).

### 10.3 Performance & Caching
#### Task 47 — Performance & Caching
- [ ] Setup a Redis cluster via Docker Compose.
- [ ] Cache heavy database queries (e.g., user's monthly expense aggregates).
- [ ] Configure a CDN setup for static frontend assets.

### 10.4 Security Monitoring & Incident Response
#### Task 48 — Incident Response
- [ ] Log all authentication events, authorization failures, and admin actions
- [ ] Set real-time alerts for: repeated auth failures, privilege escalation, unusual data export volume
- [ ] Add pre-commit hooks (gitleaks) to prevent secret leaks before they reach git
- [ ] Write an incident response plan with defined roles and escalation paths
- [ ] Create runbooks for: credential leak, DDoS, data exfiltration
- [ ] Schedule quarterly access reviews (remove stale accounts, unused API keys)
- [ ] Run `pip-audit` and `npm audit` on a recurring schedule (not just at build time)

> **🛡️ Security Ref**: See [`security-checklist.md`](architecture-study/security-checklist.md) Category 8 (Logging, Monitoring & Response) and Category 9 (Dependency & Infra Hygiene).

### ✅ Phase 10 Checkpoint
- [ ] You can view logs in a structured format.
- [ ] The API rejects requests if hit too many times in a second (429 Too Many Requests).
- [ ] Fetching dashboard stats is noticeably faster due to caching.
- [ ] Auth anomaly alerts fire on simulated attacks.
- [ ] An incident response plan exists and has been reviewed.

---

## Phase 11: Feature Expansion (Enterprise Features)

> **Objective**: Implement 9 advanced features to transform the application into an enterprise-grade personal finance tool.
>
> See also: [`architecture-study/high-level-design.md`](architecture-study/high-level-design.md) § Functional Requirements and [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for the user-facing feature overview.

### 11.1 Top Priority Features
#### Task 48 — Recurring Expenses (Subscriptions)
- [ ] Create `RecurringExpense` model and DB table.
- [ ] Implement backend endpoints to create, update, delete recurring schedules.
- [ ] Set up a background worker (e.g., Celery or APScheduler) to automatically generate expense records on the scheduled date.
- [ ] Create UI to manage active subscriptions.

#### Task 49 — Advanced Analytics & Asynchronous Data Export (SDE-3 Level)
- [ ] Backend: Build complex aggregation endpoints (Month-over-Month comparisons, heatmaps).
- [ ] Backend: Implement CSV and massive PDF tax report generation via a Background Worker Queue (Celery/Redis) to avoid blocking the API.
- [ ] Frontend: Integrate charting libraries (e.g., Recharts) and polling/WebSocket for report completion notifications.

#### Task 50 — Budgets & Alerts
- [ ] Create `Budget` model allowing users to set monthly limits per category.
- [ ] Backend: Track spending against budgets in real-time.
- [ ] Frontend: Display progress bars for budgets.
- [ ] Trigger an alert/email if a user hits 90% of their allocated budget.

### 11.2 AI & Automation
#### Task 51 — Receipt Scanning (OCR / AI)
- [ ] Integrate an external AI/Vision API (e.g., OpenAI GPT-4 Vision).
- [ ] Create an image upload endpoint that processes receipts to extract total amount, date, and merchant name.
- [ ] Auto-fill the `Add Expense` form with extracted data.

#### Task 52 — AI Spending Insights
- [ ] Setup a weekly cron job to analyze user spending patterns.
- [ ] Call LLM API to generate natural language financial advice (e.g., "You spent 20% less on dining out this month!").
- [ ] Display insights prominently on the user dashboard.

#### Task 57 — Autonomous Financial Advisor (Multi-Agent AI)

> See [`docs/AGENTIC_AI_SETUP.md`](docs/AGENTIC_AI_SETUP.md) for the full implementation guide.
- [ ] Install LangChain, LangGraph, and Core LLM dependencies.
- [ ] Define FastAPI backend Tools (using LangChain `@tool`) to safely query/mutate user data (e.g., `get_spending`, `create_budget`).
- [ ] Create a LangGraph State machine with a Supervisor Agent, Data Analyst Agent, and Action Executor Agent.
- [ ] Expose an interactive `/ai/chat` endpoint (REST or WebSocket) securely passing `current_user.id` into the LangGraph state.

#### Task 58 — Local RAG for Financial Documents
- [ ] Install local RAG dependencies (`chromadb`, `sentence-transformers`, `pypdf`).
- [ ] Create a `/documents/upload` endpoint to ingest bank statements or tax forms.
- [ ] Implement text chunking and HuggingFace embeddings generation.
- [ ] Provide the AI Analyst with a retrieval tool to query the local ChromaDB vector store.

#### Task 59 — Human-in-the-Loop (HITL) for Safety
- [ ] Add an `interrupt_before` breakpoint in the LangGraph setup for the `action_executor` node.
- [ ] Implement a WebSocket/Polling endpoint for the frontend to receive "Approval Required" payloads.
- [ ] Create an "Approve/Reject" UI component on the frontend.
- [ ] Implement a graph `resume()` endpoint on the backend to continue execution after user approval.

#### Task 60 — Self-Healing Agents
- [ ] Wrap LangChain tool executions in robust try/except blocks.
- [ ] Return error tracebacks as `ToolMessage` payloads rather than crashing the graph.
- [ ] Implement a conditional edge that loops the agent back to retry generation if a Tool Error occurs.

#### Task 61 — Voice-to-Action (Multi-Modal)
- [ ] Add a microphone UI component to the frontend `Add Expense` page.
- [ ] Use the browser's native Web Speech API (or OpenAI Whisper) to transcribe spoken expenses.
- [ ] Send the transcript to the AI pipeline to automatically parse and log the expense.

### 11.3 Advanced Transaction Tracking
#### Task 53 — Split Transactions
- [ ] Update DB schema to allow one parent `Expense` to have multiple child `SubExpense` records linked to different categories.
- [ ] Update frontend forms to support itemized entry (e.g., $70 Groceries, $30 Electronics from a single $100 receipt).

#### Task 54 — Multi-Currency Support & Live FX (SDE-3 Level)
- [ ] Update `Expense` model to track native currency, base currency (USD), and the applied exchange rate.
- [ ] Integrate an Exchange Rate API (e.g., OpenExchangeRates) to convert values.
- [ ] Setup a cron job (Celery/APScheduler) to fetch daily rates and cache them in Redis to avoid rate limits and latency.
- [ ] Frontend dropdown for currency selection.

#### Task 55 — Tags, Attachments & Geolocation
- [ ] Create a `Tag` system (many-to-many relationship with Expenses) for custom tagging (e.g., `#vacation-2026`).
- [ ] Support PDF/image attachments for invoices.
- [ ] Save GPS coordinates of where the transaction occurred.

### 11.4 Multiplayer Finance
#### Task 56 — Shared Wallets & Splitwise Features
- [ ] **Database Schema Updates**:
  - [ ] Create `Group` model and `GroupMember` association table.
  - [ ] Create `ExpenseSplit` entity mapping users to exact amounts owed.
  - [ ] Create `Settlement` entity for tracking debt payments between users.
  - [ ] Update `Expense` entity with `group_id`, `paid_by_id`, and `split_type`.
- [ ] **Settlement Engine (Debt Simplification)**:
  - [ ] Implement an algorithm to calculate net balances for all group members.
  - [ ] Implement a greedy matching algorithm to minimize transactions (Debtors to Creditors).
- [ ] **Group & Expense Endpoints**:
  - [ ] `POST /groups`, `GET /groups`, `POST /groups/{id}/members`.
  - [ ] Modify `POST /expenses` to accept `split_type` and a list of specific `ExpenseSplit` records.
  - [ ] `GET /groups/{id}/balances` to expose the simplified debt graph.
  - [ ] `POST /groups/{id}/settlements` to record a payment and clear debt.

---

## Phase 12: LaunchDarkly Feature Management

> See [`docs/launchdarkly-integration-guide.md`](docs/launchdarkly-integration-guide.md) for the full SDK setup guide and [`docs/RBAC.md`](docs/RBAC.md) for the subscription tier model.

### 12.1 Backend Integration (FastAPI)
#### Task 62 — Backend SDK Initialization & Singleton
- [ ] Install `launchdarkly-server-sdk`.
- [ ] Create `backend/app/launchdarkly_client.py`.
- [ ] Implement startup/shutdown events in `main.py` to initialize and close the LaunchDarkly client.
- [ ] Ensure the client fails gracefully if the SDK key is invalid.

#### Task 63 — Backend Context & Evaluation
- [ ] Update `feature_flags.py` to remove the old `.env` parsing logic.
- [ ] Rewrite `require_feature` dependency to build an `ldclient.Context` using `current_user.id`, `current_user.email`, and `current_user.role`.
- [ ] Implement `ldclient.get().variation()` to evaluate flags locally with zero-latency.

### 12.2 Frontend Integration (React)
#### Task 64 — Frontend Context Initialization
- [ ] Install `launchdarkly-react-client-sdk`.
- [ ] Add `VITE_LD_CLIENT_ID` to `.env`.
- [ ] Wrap the React application root in the `withLDProvider` HOC or `LDProvider` context.
- [ ] Render a loading spinner or fallback UI while the SDK initializes.

#### Task 65 — Dynamic Context Hydration
- [ ] Update `AuthContext.jsx` or the Login component to call `useLDClient().identify(context)` immediately after a successful login.
- [ ] Pass the user's ID, email, and subscription tier to LaunchDarkly to fetch personalized flag variations.
- [ ] Replace static feature checks in the UI with `useFlags()` from the React SDK.

### 12.3 Testing & CI/CD
#### Task 66 — Offline Mocking for Unit Tests
- [ ] Configure the backend SDK to use the `TestData` source in the Pytest suite to avoid network calls.
- [ ] Create a local `ld-flags.json` file for frontend developers to mock flag states without hitting the live LaunchDarkly servers.

---

## Phase 13: Testing Rigor

> **Objective**: Implement a comprehensive, multi-layered testing strategy that provides confidence in every deployment. See [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) for tool references and commands.

### 13.1 Unit Testing (Backend)
#### Task 67 — Backend Unit Test Coverage
- [x] Install `pytest-cov`: `pip install pytest-cov`.
- [x] Write `tests/test_auth.py`: cover register, verify-OTP, login, refresh, logout, brute-force lockout.
- [x] Write `tests/test_expenses.py`: cover CRUD operations, ownership enforcement (IDOR), pagination.
- [x] Write `tests/test_categories.py`: cover create, list, delete, duplicate name rejection.
- [x] Write `tests/test_rbac.py`: confirm `free` users are blocked from `pro`-gated endpoints.
- [x] Enforce coverage gate: `pytest --cov=app --cov-fail-under=80` in CI.

### 13.2 Unit Testing (Frontend)
#### Task 68 — Frontend Unit Test Setup
- [x] Install Vitest and testing library: `npm install -D vitest @testing-library/react @testing-library/user-event jsdom`.
- [x] Configure `vite.config.js` to add `test: { environment: 'jsdom' }`.
- [x] Write tests for `Login.jsx` form validation (empty fields, invalid email format).
- [x] Write tests for `Register.jsx` form validation and password matching.
- [x] Write tests for `AuthContext.jsx` token refresh logic (mock `api.js`).
- [x] Write tests for `FeatureFlagContext.jsx` flag evaluation.
- [x] Add `npx vitest run --coverage` as a CI step.

### 13.3 Integration & Contract Testing
#### Task 69 — Integration Test Suite
- [ ] Create `backend/tests/test_integration/` directory.
- [ ] Write full auth flow integration test: register → verify-OTP → login → refresh → logout.
- [ ] Write full expense lifecycle test: create → update → delete → confirm 404.
- [ ] Write cross-user isolation test: confirm User A cannot access User B's expenses.

#### Task 70 — API Contract Testing (Schemathesis)
- [ ] Install `schemathesis`: `pip install schemathesis`.
- [ ] Add `schemathesis run http://localhost:8000/openapi.json --checks all` as a CI step.
- [ ] Document any schema violations found and fix them.

### 13.4 Functional Testing
#### Task 71 — Functional Test Markers
- [ ] Add `@pytest.mark.functional` decorator to all business-rule tests.
- [x] Create a `pytest.ini` marker registration for `smoke`, `functional`, `integration`.
- [ ] Ensure all rows in the Functional Test Case Matrix in `TESTING_GUIDE.md` have a corresponding test.

### 13.5 Smoke Testing
#### Task 72 — Smoke Test Suite
- [x] Create `backend/tests/test_smoke.py` with `@pytest.mark.smoke`.
- [x] Test `GET /health` returns `200`.
- [x] Test `GET /health/db` returns `200`.
- [x] Test a register + login round-trip completes without error.
- [x] Add `pytest -m smoke` as the **first** step in the Jenkins pipeline (abort on failure).

### 13.6 End-to-End (E2E) Automation
#### Task 73 — Playwright Setup
- [ ] Create an `e2e/` directory at the project root.
- [ ] Install Playwright: `npm install -D @playwright/test && npx playwright install chromium`.
- [ ] Configure `playwright.config.ts` with baseURL, screenshot on failure, and HTML reporter.

#### Task 74 — E2E User Journey Scripts
- [ ] Write `e2e/onboarding.spec.ts`: Register → Verify OTP → Land on Dashboard.
- [ ] Write `e2e/expense-management.spec.ts`: Login → Add → Edit → Delete expense.
- [ ] Write `e2e/session-persistence.spec.ts`: Login → Close tab → Reopen → Confirm still logged in.
- [ ] Write `e2e/rbac-ui.spec.ts`: Login as free user → Confirm pro features are hidden.
- [ ] Add Playwright tests to Jenkins `staging` pipeline stage.

### 13.7 Performance Testing
#### Task 75 — Load Test Scenarios
- [ ] Expand `backend/load_tests/locustfile.py` to cover expense CRUD endpoints (not just health).
- [ ] Add a **stress test** scenario: ramp to 5,000 users over 5 minutes.
- [ ] Add a **spike test** scenario: 0 → 2,000 users in 10 seconds.
- [ ] Add a **soak test** scenario: 200 users sustained for 1 hour.
- [ ] Document pass/fail thresholds: p95 < 200ms, error rate < 1% at 500 users.

### 13.8 Security Testing
#### Task 76 — SAST & Dependency Scanning
- [ ] Install and run `bandit -r backend/app/ -ll`; fix any HIGH severity findings.
- [ ] Install and run `pip-audit -r backend/config/requirements.txt`; update vulnerable packages.
- [ ] Run `npm audit --audit-level=high` in `frontend/`; fix any HIGH severity findings.
- [ ] Add Bandit + pip-audit + npm audit as CI steps (fail on HIGH severity).

#### Task 77 — Secret Scanning (Gitleaks)
- [ ] Add Gitleaks scan as a pre-commit hook.
- [ ] Add Gitleaks Docker scan to Jenkins pipeline.
- [ ] Confirm no secrets are committed in the repo history.

#### Task 78 — DAST & Container Scanning
- [ ] Run OWASP ZAP baseline scan against staging: `docker run owasp/zap2docker-stable zap-baseline.py -t <staging-url>`.
- [ ] Run Trivy image scan on `expense-tracker-backend:latest`.
- [ ] Run Trivy image scan on `expense-tracker-frontend:latest`.
- [ ] Fix any CRITICAL or HIGH CVEs found.

#### Task 79 — Manual Security Test Cases
- [ ] Execute all manual security test cases from `TESTING_GUIDE.md §8.4`.
- [ ] Document results in a `docs/SECURITY_TEST_RESULTS.md` file.
- [ ] Verify brute-force lockout triggers after 5 failed login attempts.
- [ ] Verify IDOR protection: confirm User A's JWT cannot access User B's expenses.

### 13.9 Chaos Engineering
#### Task 80 — Chaos Test Runbook
- [ ] Document a chaos runbook in `docs/CHAOS_RUNBOOK.md`.
- [ ] Execute DB failure scenario: `docker compose stop db` → confirm `503` response.
- [ ] Execute Redis failure scenario: `docker compose stop redis` → confirm app continues.
- [ ] Execute memory limit scenario: set Docker memory to 64MB → confirm container restarts cleanly.

### 13.10 Accessibility Testing
#### Task 81 — a11y Audit
- [ ] Install `@axe-core/playwright`: `npm install -D @axe-core/playwright`.
- [ ] Write `e2e/a11y.spec.ts` that runs axe against Login, Register, Dashboard, and Add Expense pages.
- [ ] Fix all WCAG 2.1 AA violations (focus order, colour contrast, ARIA labels).

---

## 🎓 You've Graduated!

If you've completed all phases, you have:

1. **Built** a production-grade REST API with async database operations
2. **Connected** it to a managed PostgreSQL database
3. **Implemented** persistent JWT authentication with refresh tokens
4. **Created** a React frontend with routing and centralized API calls
5. **Containerized** the full stack with Docker Compose
6. **Deployed** to a cloud platform with proper security hardening
7. **Tested** both backend and frontend with automated test suites
8. **Automated** the entire build/test/deploy cycle with CI/CD
9. **Architected** advanced enterprise features like AI, OCR, asynchronous workers, and complex data aggregations.

These are the core competencies of a software architect. The next step is to apply these patterns to larger, more complex systems.
