# Testing Guide

> See also: [Security Checklist](../architecture-study/security-checklist.md) · [TODO.md](../TODO.md) · [Observability Guide](OBSERVABILITY_GUIDE.md) · [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

This guide is the single source of truth for all testing methodologies used in the Expense Tracker project. It covers every layer of the testing pyramid — from fast unit tests to deep security penetration tests — and maps each to the appropriate tooling and CI/CD integration point.

---

## Testing Strategy Overview

```
                      ┌────────────────────────┐
                      │  Security / Pen Tests   │ ← OWASP ZAP, Bandit, Trivy
                      ├────────────────────────┤
                      │    E2E / Automation     │ ← Playwright
                      ├────────────────────────┤
                      │   Integration Testing   │ ← Pytest (cross-service)
                      ├────────────────────────┤
                 ┌────┴─────────────────────────┴────┐
                 │  Unit Testing (Backend + Frontend)  │ ← Pytest, Vitest
                 └────────────────────────────────────┘
```

**Pipeline Order**: Smoke → Unit → Integration → Regression → E2E → Security → Performance

---

## 1. Unit Testing

Unit tests verify that individual functions and endpoints behave correctly in isolation.

### 1.1 Backend Unit Tests (Pytest)

- **Framework**: `pytest` + `pytest-asyncio`
- **HTTP Client**: `httpx.AsyncClient` for simulating requests against the FastAPI app
- **Database Strategy**: Tests run against a real PostgreSQL database. Every test is wrapped in a **nested transaction** (via `conftest.py`) that is rolled back on completion, leaving the DB pristine.
- **Mocking**: `unittest.mock.patch` mocks external services (Resend emails, BackgroundTasks) for hermetic, fast tests.

```bash
cd backend
pytest -v                                    # Run all tests with verbose output
pytest -v --cov=app --cov-report=html        # With HTML coverage report
pytest -v -k "auth"                          # Filter tests by name
pytest -v tests/test_expenses.py             # Run a specific test file
```

**Coverage target**: ≥ 80% for all critical business logic (`auth.py`, `expense_routes.py`, `category_routes.py`).

#### Writing New Backend Tests
1. Create `backend/tests/test_<feature>.py`.
2. Decorate async tests with `@pytest.mark.asyncio`.
3. Use the `client` fixture for HTTP requests and `db_session` for direct DB queries.

### 1.2 Frontend Unit Tests (Vitest)

- **Framework**: `Vitest` (Vite-native, Jest-compatible API)
- **Component Testing**: `@testing-library/react` for rendering and simulating user interactions
- **Mocking**: `vi.mock()` for the `api.js` service layer and context providers

```bash
cd frontend
npx vitest run              # Run all tests once
npx vitest                  # Watch mode
npx vitest --coverage       # V8 coverage report
```

**What to test**:
- Auth form validation (Login, Register — empty fields, bad email format)
- `AuthContext` token refresh logic
- `FeatureFlagContext` flag evaluation
- Component rendering with mocked API responses (Dashboard chart data)

---

## 2. Integration Testing

Integration tests verify that multiple layers (API + DB, auth middleware + route handlers) work together without mocking infrastructure.

### 2.1 Backend Integration Tests (Pytest)

Uses the same Pytest suite but exercises multi-step flows:
- **Auth flow**: `POST /auth/register` → `POST /auth/verify-otp` → `POST /auth/login` → `POST /auth/refresh` → `POST /auth/logout`
- **Expense lifecycle**: Create → Fetch list → Update → Delete → Verify 404
- **RBAC enforcement**: Confirm `free` users are blocked from `pro`-gated endpoints

```bash
cd backend
pytest -v tests/test_integration/
```

### 2.2 API Contract Testing (Schemathesis)

Auto-generates and runs hundreds of test cases from the FastAPI OpenAPI spec. Catches schema drift between frontend expectations and backend implementation.

```bash
pip install schemathesis
schemathesis run http://localhost:8000/openapi.json --checks all
```

---

## 3. Functional Testing

Functional tests verify that the system satisfies its stated business requirements — what the system does, not how.

### Test Case Matrix

| Feature | Scenario | Expected Result |
|---|---|---|
| **Registration** | Valid new user | `201 Created`, OTP email sent |
| **Registration** | Duplicate email | `409 Conflict` |
| **Registration** | Disposable email | `422 Unprocessable Entity` |
| **Login** | Correct credentials | `200 OK`, access + refresh tokens |
| **Login** | Wrong password (5×) | `429 Too Many Requests`, account locked |
| **Login** | Unverified account | `403 Forbidden` |
| **OTP Verification** | Correct OTP | `200 OK`, tokens issued |
| **OTP Verification** | Expired OTP | `400 Bad Request` |
| **Expense Create** | Valid payload | `201 Created`, appears in GET list |
| **Expense Read** | Another user's expense | `403 Forbidden` |
| **Expense Delete** | Non-existent ID | `404 Not Found` |
| **Categories** | Duplicate name | `409 Conflict` |
| **RBAC** | `free` user hits `pro` endpoint | `403 Forbidden` |

```bash
pytest -v tests/ -m "functional"    # Requires @pytest.mark.functional marker
```

---

## 4. Smoke Testing

Smoke tests are the first gate after any deployment. They verify the system is alive in under **30 seconds**. If they fail, the pipeline aborts immediately.

```bash
# API is alive
curl -f http://localhost:8000/health

# Database connection is healthy
curl -f http://localhost:8000/health/db

# Run smoke test suite
pytest -v tests/ -m "smoke"
```

**Smoke test scope**: Health endpoints, auth register + login round-trip, expense list returns 200.

---

## 5. Regression Testing

Regression tests ensure previously working features are not broken by new code. The full regression suite runs automatically on every PR.

- **Backend**: Full `pytest` suite acts as the regression suite.
- **Frontend**: Full `vitest` suite.
- **Coverage gate**: CI fails if line coverage drops below 80%.

```bash
# Backend regression
cd backend && pytest -v --cov=app --cov-fail-under=80

# Frontend regression
cd frontend && npx vitest run --coverage
```

---

## 6. End-to-End (E2E) & Automation Testing

E2E tests simulate complete real-user journeys through the browser, exercising the full stack (React → Vite Proxy → FastAPI → PostgreSQL).

- **Tool**: `Playwright`
- **Location**: `e2e/` directory at the project root

```bash
# Install
pip install playwright && playwright install chromium
# Or: npm install -D @playwright/test && npx playwright install

# Run all journeys
playwright test

# Debug with UI mode
playwright test --ui

# Generate HTML report
playwright test --reporter=html
```

### Key Journeys to Automate

| Journey | Steps |
|---|---|
| **New User Onboarding** | Navigate to Register → Fill form → Submit → Verify OTP → Land on Dashboard |
| **Expense Management** | Login → Add Expense → Edit Expense → Delete Expense → Verify list |
| **Category Flow** | Login → Create Category → Assign to Expense → Delete Category |
| **Session Persistence** | Login → Close tab → Reopen → Confirm still logged in via refresh token |
| **Logout** | Login → Logout → Confirm redirect to Login → Confirm token cleared |
| **RBAC UI** | Login as `free` user → Confirm `pro` features are hidden/disabled |

---

## 7. Performance Testing

### 7.1 Load Testing (Locust)

Verifies the system handles expected concurrent traffic without degradation.

```bash
cd backend
locust -f load_tests/locustfile.py
# Open http://localhost:8089 → Users: 1000, Spawn Rate: 50/s
```

**Pass criteria**: p95 response time < 200ms, error rate < 1% at 500 concurrent users.

### 7.2 Stress Testing

Finds the breaking point — the load at which errors begin to occur.

```bash
locust -f load_tests/locustfile.py --headless -u 5000 -r 100 --run-time 5m
```

Observe at what user count the error rate exceeds 5% or latency exceeds 500ms.

### 7.3 Spike Testing

Simulates a sudden traffic burst (e.g., a marketing campaign goes live).

```bash
locust -f load_tests/locustfile.py --headless -u 2000 -r 200 --run-time 2m
```

### 7.4 Soak / Endurance Testing

Detects memory leaks, connection pool exhaustion, and resource creep over time.

```bash
# 200 users sustained for 1 hour
locust -f load_tests/locustfile.py --headless -u 200 -r 10 --run-time 1h
```

---

## 8. Security Testing

### 8.1 Static Application Security Testing (SAST)

Scans source code for known vulnerability patterns without running the app.

```bash
# Python SAST
pip install bandit
bandit -r backend/app/ -ll

# Python dependency vulnerability scan
pip install pip-audit
pip-audit -r backend/config/requirements.txt

# JavaScript dependency audit
cd frontend && npm audit
```

### 8.2 Dynamic Application Security Testing (DAST)

Tests the running application by actively sending attack payloads.

```bash
# OWASP ZAP Baseline scan (passive — safe for staging)
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000

# Full active scan (aggressive — use only on dev/staging)
docker run -t owasp/zap2docker-stable zap-full-scan.py -t http://localhost:8000
```

### 8.3 Container Image Scanning (Trivy)

```bash
trivy image expense-tracker-backend:latest
trivy image expense-tracker-frontend:latest
```

### 8.4 Manual Security Test Cases

| Attack | How to Test | Expected Result |
|---|---|---|
| **SQL Injection** | Send `' OR 1=1 --` in `description` field | `422` — Pydantic schema rejects |
| **Brute Force** | POST `/auth/login` wrong password 6× | `429` after 5th, account locked |
| **JWT Tampering** | Modify JWT payload, re-sign with wrong secret | `401 Unauthorized` |
| **IDOR** | GET `/expenses/{other_user_expense_id}` | `403 Forbidden` |
| **Expired Token** | Use access token after 15 minutes | `401 Unauthorized` |
| **CORS Bypass** | Request from `Origin: http://evil.com` | No credentials returned |
| **Mass Assignment** | Send extra fields in expense body | Extra fields silently ignored |
| **Path Traversal** | Upload file with name `../../etc/passwd` | `422` rejection |

### 8.5 Secret Scanning (Gitleaks)

```bash
docker run -v ${PWD}:/path zricethezav/gitleaks:latest detect --source=/path -v
```

---

## 9. Chaos Engineering

Validates graceful degradation and recovery from infrastructure failures.

| Failure Scenario | How to Simulate | Expected System Behaviour |
|---|---|---|
| **Database down** | `docker compose stop db` | API returns `503 Service Unavailable` |
| **DB pool exhausted** | 200+ concurrent requests | Requests queue; no crash |
| **Redis down** | `docker compose stop redis` | Rate limiting skipped; app continues; warning logged |
| **Backend OOM** | Set Docker memory limit to 64MB | Container restarts; health check recovers it |
| **Slow DB query** | Inject `pg_sleep(5)` | Request times out; other requests unaffected (async) |
| **Network partition** | `docker network disconnect` | Appropriate timeout errors returned |

---

## 10. Accessibility Testing (a11y)

Ensures the frontend meets **WCAG 2.1 AA** standards.

```bash
cd frontend
npm install @axe-core/playwright
npx playwright test --grep "@a11y"
```

**Key checks**: All form inputs have associated labels, colour contrast ≥ 4.5:1, full keyboard navigation, ARIA roles on dynamic content, screen reader compatibility.

---

## CI/CD Pipeline Integration

```
 Push to Branch
      │
      ▼
 ┌─────────────┐
 │ Smoke Tests │ ← Abort pipeline immediately if health checks fail
 └──────┬──────┘
        ▼
 ┌─────────────────┐
 │ SAST + Auditing │ ← Bandit, pip-audit, npm audit, Gitleaks
 └──────┬──────────┘
        ▼
 ┌────────────────────────────┐
 │ Unit + Regression Tests    │ ← pytest --cov (gate: 80%), vitest --coverage
 └──────┬─────────────────────┘
        ▼
 ┌────────────────────┐
 │ Integration Tests  │ ← Pytest cross-service + schemathesis contract tests
 └──────┬─────────────┘
        ▼
 ┌────────────────┐   (staging only)
 │  E2E Tests     │ ← Playwright user journeys
 └──────┬─────────┘
        ▼
 ┌──────────────────┐   (staging only)
 │ DAST + Container │ ← OWASP ZAP baseline, Trivy image scan
 └──────┬───────────┘
        ▼
   Deploy to Env
```

---

## 🔗 See Also

- [Security Checklist](../architecture-study/security-checklist.md) — OWASP ASVS § 10-11 (QA & Security testing requirements)
- [TODO.md](../TODO.md) — Phase 8 (Testing Rigor) and Phase 9 (CI/CD) tasks
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) — Pre-deploy test verification steps
- [Observability Guide](OBSERVABILITY_GUIDE.md) — Monitoring and alerting on test failures
- **Key code files**: [`backend/tests/`](../backend/tests/), [`backend/load_tests/`](../backend/load_tests/), [`backend/app/database.py`](../backend/app/database.py)
