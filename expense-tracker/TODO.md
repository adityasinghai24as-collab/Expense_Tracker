# 📋 Expense Tracker — SDE-2 Development Guide

> **Goal**: Work through each phase sequentially. Each phase builds on the last.
> Check off tasks as you complete them. By the end, you will have a production-deployed, tested, full-stack application with a CI/CD pipeline.
>
> **Security Standard**: This project targets **OWASP ASVS Level 2** compliance.
> See [`architecture-study/security-checklist.md`](architecture-study/security-checklist.md) for the full 19-section deployment hardening checklist.

---

## Legend

- `[ ]` — Not started
- `[/]` — In progress
- `[x]` — Complete

---

## Phase 1: Backend — Get the API Server Running Locally

> **Objective**: Start the FastAPI backend on your machine and confirm the health endpoint responds.

### 1.1 Environment Setup
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
- [x] Read through `main.py` — understand how FastAPI initializes, adds CORS middleware, and registers routes
- [x] Read through `app/schemas.py` — understand how Pydantic models validate request/response data
- [x] Read through `app/models.py` — understand how SQLAlchemy ORM models map to database tables
- [x] Read through `app/database.py` — this is where most of your upcoming work will happen

> **🧠 Architect's Note**: Notice how `main.py` imports from `app.database` but never touches raw SQL. This is the *Dependency Inversion Principle* in action — your API layer depends on abstractions (`get_db`), not concrete database details. This separation is what makes the backend testable, swappable, and scalable.

### ✅ Phase 1 Checkpoint
- [x] `http://localhost:8000/health` returns `{"status": "ok", ...}`
- [x] You can articulate what each file in `backend/app/` is responsible for

---

## Phase 2: Database — Connect PostgreSQL

> **Objective**: Stand up a PostgreSQL instance via Docker, then implement the database connection layer in `app/database.py`.

### 2.1 Start the Database with Docker
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

Open `backend/app/database.py`. You will complete **Tasks 1-6** in order.

#### Task 1 — Database Configuration (URL Construction)
- [x] Read `DATABASE_URL` from env vars. If it exists, use it directly.
- [x] If not, read individual `DB_*` vars and construct the connection strings:
  ```
  SYNC_DATABASE_URL  = "postgresql://{user}:{password}@{host}:{port}/{name}"
  ASYNC_DATABASE_URL = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
  ```

> **🧠 Architect's Note**: We support two modes because Docker Compose injects a full `DATABASE_URL`, but local development uses individual vars from a `.env` file. Supporting both means zero config changes between environments. This is called *environment parity* — a key principle from the [Twelve-Factor App](https://12factor.net/).

#### Task 2 — Create the Async Engine and Session Factory
- [x] Use `create_async_engine(ASYNC_DATABASE_URL, ...)` to create `async_engine`
- [x] Use `sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)` to create `AsyncSessionLocal`

> **🧠 Architect's Note**: `expire_on_commit=False` prevents SQLAlchemy from lazily re-fetching data after a commit, which would fail in an async context. This is a common gotcha. The `pool_pre_ping=True` option ensures stale connections are detected before queries, preventing cryptic "connection closed" errors in production.

#### Task 3 — Implement `get_db()` (Dependency Injection)
- [x] Make it an `async` generator that yields an `AsyncSession`
- [x] Use `async with AsyncSessionLocal() as session:` and `try/finally` to ensure cleanup

> **🧠 Architect's Note**: FastAPI calls this function via its `Depends()` system. Every route that needs the database declares `db: AsyncSession = Depends(get_db)`. This means your route functions *never* create or manage sessions themselves. That's Inversion of Control — the framework manages the resource lifecycle, not your business logic.

#### Task 4 — Implement `check_db_connection()` (Async Health Check)
- [x] Use `asyncpg.connect(...)` to open a raw async connection
- [x] Execute `SELECT 1` to prove the connection works
- [x] Close the connection and return `(True, "Connected successfully")`
- [x] Wrap in `try/except` and return `(False, str(error))` on failure

#### Task 5 — Implement `check_db_connection_sync()` (Sync Health Check)
- [x] Use `create_engine(SYNC_DATABASE_URL, poolclass=NullPool)` for a throwaway engine
- [x] Execute `text("SELECT 1")` inside `engine.connect()`
- [x] Dispose the engine and return the result tuple

#### Task 6 — Implement `init_db()` (Table Creation)
- [x] Use `async with async_engine.begin() as conn:` to get a connection
- [x] Run `await conn.run_sync(Base.metadata.create_all)` to create all tables

### 2.4 Verify End-to-End Database Connection
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
- [x] Add to `backend/config/requirements.txt`:
  ```
  python-jose[cryptography]==3.3.0
  passlib[bcrypt]==1.7.4
  ```
- [x] Run `pip install -r backend/config/requirements.txt`

### 3.2 Add Password Field to User Model

#### Task 10 — Update User Model for Auth
- [x] Open `backend/app/models.py`
- [x] Add `hashed_password` column (String, nullable=False) to the User model
- [x] Add `refresh_token` column (String, nullable=True) — stores the current valid refresh token
- [x] Add `token_expires_at` column (DateTime, nullable=True) — when the refresh token expires

> **🧠 Architect's Note**: Storing the refresh token hash in the DB lets you implement "logout everywhere" — just clear the column and all existing refresh tokens become invalid. This is how Google/GitHub handle session revocation.

### 3.3 Create Auth Schemas

#### Task 11 — Auth Request/Response Schemas
- [x] Open `backend/app/schemas.py`
- [x] Add `UserLogin` schema (email, password)
- [x] Add `TokenResponse` schema (access_token, refresh_token, token_type)
- [x] Add `TokenRefreshRequest` schema (refresh_token)
- [x] Update `UserCreate` to include a `password` field (plain text input, will be hashed before storage)

### 3.4 Implement the Auth Module

#### Task 12 — Create `backend/app/auth.py`
- [ ] Create a new file `backend/app/auth.py`
- [ ] Implement `hash_password(password: str) -> str` using passlib/bcrypt
- [ ] Implement `verify_password(plain: str, hashed: str) -> bool`
- [ ] Implement `create_access_token(data: dict) -> str` — short-lived JWT (15-30 min)
- [ ] Implement `create_refresh_token(data: dict) -> str` — long-lived JWT (7-30 days)
- [ ] Implement `decode_token(token: str) -> dict` — verifies and decodes a JWT
- [ ] Read `SECRET_KEY` and `ALGORITHM` from env vars
- [ ] Use bcrypt with cost factor ≥ 12 (OWASP recommendation; Argon2id preferred if passlib supports it)
- [ ] Enforce strong password policy: min 12 chars, check against HaveIBeenPwned Pwned Passwords API (**not** arbitrary complexity rules like "must include uppercase + symbol")

> **🛡️ Security Ref**: See `security-checklist.md` §3 (Authentication) and §11 (Session Management) for the full requirements.

> **🧠 Architect's Note**: Access tokens are short-lived (15 min) and sent with every API request. Refresh tokens are long-lived (7+ days) and stored in an HttpOnly cookie — this is what makes login "persistent". The browser automatically sends the cookie, so the user never has to re-enter credentials unless the refresh token expires or is revoked.

#### Task 13 — Create Auth Middleware / Dependency
- [ ] Implement `get_current_user(token: str = Depends(oauth2_scheme))` dependency
- [ ] This should decode the access token, look up the user in the DB, and return the User object
- [ ] Return 401 if the token is expired or invalid

#### Task 14 — Create Auth Endpoints
- [ ] `POST /auth/register` — Create a new user (hash password before storing)
- [ ] `POST /auth/login` — Verify credentials, return access + refresh tokens
  - Set refresh token in an HttpOnly, Secure, SameSite cookie
  - Also store the refresh token hash in the user's DB row
- [ ] `POST /auth/refresh` — Accept refresh token (from cookie), validate it against DB, return new access token
- [ ] `POST /auth/logout` — Clear the refresh token from DB and delete the cookie
- [ ] `GET /auth/me` — Return the current user's profile (protected route)
- [ ] Implement account lockout / exponential backoff after 5 failed login attempts (security-checklist §3)
- [ ] Set cookies with `HttpOnly`, `Secure`, `SameSite=Lax` flags (security-checklist §11)
- [ ] Rotate refresh token on every use (issue new token on each `/auth/refresh` call)

### 3.5 Frontend Persistent Login

#### Task 15 — Auth Context and Token Management
- [ ] Create `frontend/src/context/AuthContext.jsx`
- [ ] Store access token in memory (React state) — NOT in localStorage (XSS risk)
- [ ] On app load, call `POST /api/auth/refresh` to get a new access token from the HttpOnly cookie
  - If successful → user is "still logged in" (persistent login)
  - If failed → redirect to login page
- [ ] Create `useAuth()` hook that provides: `user`, `login()`, `logout()`, `isAuthenticated`
- [ ] Add an Axios/fetch interceptor that:
  - Attaches the access token to every request (`Authorization: Bearer <token>`)
  - On 401 response, automatically calls `/auth/refresh` and retries the request

#### Task 16 — Login and Register Pages
- [ ] Create `frontend/src/pages/Login.jsx` — email + password form
- [ ] Create `frontend/src/pages/Register.jsx` — email + password + username form
- [ ] Add routes for `/login` and `/register`
- [ ] Redirect to dashboard after successful login
- [ ] Add a `ProtectedRoute` wrapper component that redirects to `/login` if not authenticated

### 3.6 Verify Authentication End-to-End
- [ ] Register a new user via `POST /auth/register`
- [ ] Login and confirm you receive tokens
- [ ] Close the browser tab, reopen — confirm you are still logged in (refresh token cookie persists)
- [ ] Hit a protected endpoint — confirm it works with the access token
- [ ] Logout — confirm the refresh token is invalidated

### ✅ Phase 3 Checkpoint (Auth)
- [ ] Users can register and login
- [ ] Login persists across browser sessions (refresh token in HttpOnly cookie)
- [ ] Protected routes reject unauthenticated requests with 401
- [ ] Logout invalidates the session server-side
- [ ] Passwords are hashed with bcrypt (cost ≥ 12); weak passwords are rejected
- [ ] Failed login attempts trigger exponential backoff

---

## Phase 4: Backend — Build the CRUD API

> **Objective**: Implement the core REST endpoints for Users and Expenses. All expense endpoints should be protected (require authentication).

### 4.1 User Endpoints
- [ ] `GET /users` — List all users (admin only, return `list[UserResponse]`)
- [ ] `GET /users/{user_id}` — Get a single user by ID
- [ ] `PUT /admin/users/{user_id}/features` — Update user's feature flags (Admin only)

> **🧠 Architect's Note**: User creation is now handled by `POST /auth/register` (Phase 3). These endpoints are for user management, not registration.

> **🧠 Architect's Note**: Decide whether to keep routes in `main.py` or create a `backend/app/routers/` directory with separate files like `users.py` and `expenses.py`. The router approach scales better — it's how every production FastAPI app organizes its code. Use `APIRouter` and include it in `main.py` with `app.include_router(...)`.

### 4.2 Expense Endpoints (Protected)
- [ ] `POST /expenses` — Create a new expense (user_id derived from auth token)
- [ ] `GET /expenses` — List current user's expenses (add query params for filtering by `category`)
- [ ] `GET /expenses/{expense_id}` — Get a specific expense (must belong to current user)
- [ ] `PUT /expenses/{expense_id}` — Update an expense (must belong to current user)
- [ ] `DELETE /expenses/{expense_id}` — Delete an expense (must belong to current user)

### 4.3 Error Handling
- [ ] Return `401` when authentication fails
- [ ] Return `403` when user tries to access another user's data
- [ ] Return `404` when a user or expense is not found
- [ ] Return `422` for validation errors (Pydantic does this automatically)
- [ ] Add a global exception handler for unexpected `500` errors

### 4.4 Verify with Swagger
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
- [ ] Navigate to `expense-tracker/frontend/`
- [ ] Install dependencies: `npm install`
- [ ] Start the dev server: `npm run dev`
- [ ] Open `http://localhost:5173` — you should see the existing shell page

### 5.2 Implement the Backend Health Check (Task 7)
- [ ] Open `frontend/src/App.jsx`
- [ ] Complete **Task 7**: implement the `fetch('/api/health')` call
- [ ] Handle the JSON response and update `isConnected` / `setError` state
- [ ] Uncomment the `setInterval` polling for live connection status
- [ ] Verify: the status indicator should turn **green** when the backend is running

> **🧠 Architect's Note**: Look at `vite.config.js` — the `/api` proxy rewrites `/api/health` to `http://localhost:8000/health`. This means your frontend code never hardcodes the backend URL. In production, you'd replace this proxy with a real reverse proxy (like Nginx or Cloudflare) or use environment-based `VITE_API_URL` variables.

### 5.3 Setup Feature Flags Context
- [ ] Create `frontend/src/context/FeatureFlagContext.jsx` to parse and provide the user's `features_enabled` globally.
- [ ] Implement a `useFeatureFlag` hook to conditionally render UI elements (like AI buttons).

### 5.4 Build the Core Pages
- [ ] **Dashboard Page** — Show total expenses, expense breakdown by category, recent transactions
- [ ] **Add Expense Page** — A form with amount, description, category fields. `POST` to `/api/expenses`
- [ ] **Expense List Page** — Fetch and display all expenses from `GET /api/expenses`. Add filter/sort controls.
- [ ] **User Profile Page** — Show user info from `GET /api/users/{id}`

### 5.5 Add Client-Side Routing
- [ ] Install React Router: `npm install react-router-dom`
- [ ] Set up routes for Dashboard (`/`), Add Expense (`/add`), Expense List (`/expenses`), Profile (`/profile`)
- [ ] Add a navigation bar component shared across all pages

### 5.6 Create a Reusable API Service Layer
- [ ] Create `frontend/src/services/api.js`
- [ ] Centralize all `fetch` calls (e.g., `getExpenses()`, `createExpense(data)`, `deleteExpense(id)`)
- [ ] Handle errors consistently (toast notifications, error boundaries)

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
- [ ] Stop any locally running backend/database processes
- [ ] Run: `docker compose up -d` (from `expense-tracker/`)
- [ ] Verify both services are up: `docker compose ps`
- [ ] Test: `curl http://localhost:8000/health/db`

### 6.2 Add Frontend to Docker Compose (Stretch)
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
- [x] Create `backend/app/feature_flags.py` module
- [x] Define per-environment flag defaults in `environments/*.tfvars`
- [x] Inject `FEATURE_FLAGS` JSON env var into Cloud Run via Terraform
- [ ] Add `GET /admin/feature-flags` endpoint to `main.py`
- [ ] Gate experimental features (receipt scanning, smart categorization) behind flags

### 7.4 Production Hardening Checklist
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

> **🛡️ Security Ref**: See `security-checklist.md` §6 (Data Protection), §7 (Network Security), §12 (Security Headers), and §14 (Database Security).

### ✅ Phase 7 Checkpoint
- [ ] Backend API is reachable on a public URL and connected to the production database
- [ ] Frontend is deployed and talking to the production backend
- [ ] Health check returns `"status": "ok"` on the live URL

---

## Phase 8: Testing — Add Automated Tests

> **Objective**: Write unit and integration tests to ensure code correctness and prevent regressions.

### 8.1 Backend Tests (pytest)
- [ ] Install test dependencies: `pip install pytest pytest-asyncio httpx`
- [ ] Create `backend/tests/` directory with `__init__.py` and `conftest.py`
- [ ] Write a test fixture that provides a test database session (use an in-memory SQLite or a separate test PostgreSQL DB)
- [ ] Write tests for:
  - [ ] `GET /health` returns 200
  - [ ] `POST /users` creates a user and returns 201
  - [ ] `POST /expenses` creates an expense linked to a user
  - [ ] `GET /expenses` returns the correct list
  - [ ] `DELETE /users/{id}` cascades and deletes related expenses
  - [ ] Invalid data returns 422

> **🧠 Architect's Note**: Test against the *API contract* (HTTP status codes, response shapes), not internal implementation. This lets you refactor internals freely without rewriting tests. Use `httpx.AsyncClient` with FastAPI's `TestClient` for async endpoint testing.

### 8.2 Frontend Tests (Vitest)
- [ ] Install test dependencies: `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`
- [ ] Configure Vitest in `vite.config.js`
- [ ] Write tests for:
  - [ ] API service functions mock `fetch` and return expected data
  - [ ] Components render correctly with given props
  - [ ] Form submission calls the correct API function

### 8.3 Load Testing (Locust / k6)
- [ ] Install a load testing tool like Locust (`pip install locust`) or k6.
- [ ] Create a `load_tests/` directory with a load testing script (e.g., `locustfile.py`).
- [ ] Write tests to simulate hundreds to thousands of concurrent users performing typical workflows (login, view dashboard, add expense).
- [ ] Measure and ensure 95th percentile response times are under 200ms during peak load.
- [ ] Identify any database bottlenecks or slow queries.

### ✅ Phase 8 Checkpoint
- [ ] `pytest` passes all backend tests
- [ ] `npx vitest run` passes all frontend tests
- [ ] Load tests verify stable performance under simulated traffic of 500-1000+ users
- [ ] You understand the difference between unit tests, integration tests, and end-to-end tests

---

## Phase 9: CI/CD — Automate Everything

> **Objective**: Set up a Jenkins CI/CD pipeline that tests, builds, and deploys on every push.

### 9.1 Create the CI Pipeline
- [x] Create `Jenkinsfile` with declarative pipeline
- [x] Define stages:
  - **Code Quality**: `ruff` (Python) + `eslint` (JS) + SonarQube
  - **Security Scans**: Trivy vulnerability scanner
  - **Unit Tests**: `pytest` (backend) + `vitest` (frontend)
- [x] Pipeline triggers on pushes to `develop`, `staging`, and `main`
- [x] Security scans must pass as a merge gate

> **🛡️ Security Ref**: See `security-checklist.md` §1 (Secure SDLC), §9 (CI/CD Pipeline Security), and §17 (Pre-Launch Testing).

### 9.2 Create the CD Pipeline (Multi-Environment)
- [x] Add **Build & Push** stage to push Docker image to Artifact Registry
- [x] Add **Deploy Infrastructure** stage to run Terraform with `environments/<env>.tfvars`
- [x] Add **Post-Deploy Smoke Test** stage for health check verification
- [x] Auto-detect environment from branch (`develop`→dev, `staging`→staging, `main`→prod)
- [x] Add **manual approval gate** before production deployments
- [x] Create `docs/DEPLOYMENT_CHECKLIST.md` with pre/post-deploy steps and rollback procedures

### 9.3 Branch Protection
- [ ] Enable branch protection on `main`
- [ ] Require CI to pass before merging PRs
- [ ] Require at least 1 code review before merging

### ✅ Phase 9 Checkpoint
- [x] Every push triggers automated tests
- [x] Merging to `main` automatically deploys to production (with approval)
- [x] Multi-environment deployments are fully automated

---

## Phase 10: Enterprise Readiness (Advanced)

> **Objective**: Hardening the application for enterprise usage (observability, security, resilience).

### 10.1 Observability
- [ ] Add structured JSON logging (e.g., using `structlog` in Python).
- [ ] Integrate a monitoring/error tracking tool (e.g., Sentry) on both backend and frontend.

### 10.2 Security & Rate Limiting
- [ ] Implement Rate Limiting on the backend API (e.g., using `slowapi` or Redis).
- [ ] Setup Audit Logging for critical actions (e.g., changing passwords or permissions).

### 10.3 Performance & Caching
- [ ] Setup a Redis cluster via Docker Compose.
- [ ] Cache heavy database queries (e.g., user's monthly expense aggregates).
- [ ] Configure a CDN setup for static frontend assets.

### 10.4 Security Monitoring & Incident Response
- [ ] Log all authentication events, authorization failures, and admin actions
- [ ] Set real-time alerts for: repeated auth failures, privilege escalation, unusual data export volume
- [ ] Add pre-commit hooks (gitleaks) to prevent secret leaks before they reach git
- [ ] Write an incident response plan with defined roles and escalation paths
- [ ] Create runbooks for: credential leak, DDoS, data exfiltration
- [ ] Schedule quarterly access reviews (remove stale accounts, unused API keys)
- [ ] Run `pip-audit` and `npm audit` on a recurring schedule (not just at build time)

> **🛡️ Security Ref**: See `security-checklist.md` §10 (Logging/Monitoring), §18 (Incident Response), and §19 (Ongoing Hygiene).

### ✅ Phase 10 Checkpoint
- [ ] You can view logs in a structured format.
- [ ] The API rejects requests if hit too many times in a second (429 Too Many Requests).
- [ ] Fetching dashboard stats is noticeably faster due to caching.
- [ ] Auth anomaly alerts fire on simulated attacks.
- [ ] An incident response plan exists and has been reviewed.

---

## 🎓 You've Graduated!

If you've completed all 10 phases, you have:

1. **Built** a production-grade REST API with async database operations
2. **Connected** it to a managed PostgreSQL database
3. **Implemented** persistent JWT authentication with refresh tokens
4. **Created** a React frontend with routing and centralized API calls
5. **Containerized** the full stack with Docker Compose
6. **Deployed** to a cloud platform with proper security hardening
7. **Tested** both backend and frontend with automated test suites
8. **Automated** the entire build/test/deploy cycle with CI/CD

These are the core competencies of a software architect. The next step is to apply these patterns to larger, more complex systems.
