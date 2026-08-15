# Expense Tracker - Low Level Design (LLD)

> See also: [High-Level Design](high-level-design.md) · [Security Checklist](security-checklist.md) · [TODO.md](../TODO.md) · [PROJECT_STATE.md](../PROJECT_STATE.md)

## 1. Design Patterns

To ensure a clean, maintainable, and scalable codebase, the following design patterns will be utilized:

*   **Dependency Injection (DI)**: Extensively used in FastAPI. Database sessions (`get_db`) and authentication dependencies are injected into route handlers. This decouples the business logic from infrastructure concerns and makes unit testing significantly easier (as dependencies can be mocked).
*   **Repository Pattern (Planned)**: Data access logic will be abstracted behind repository classes (e.g., `UserRepository`, `ExpenseRepository`). This isolates the SQLAlchemy ORM specifics from the route handlers, allowing for easier query reuse and potential swapping of the underlying database technology.
*   **Data Transfer Objects (DTOs)**: Implemented using Pydantic schemas. Incoming requests are parsed and validated into DTOs (`UserCreate`, `ExpenseCreate`) before hitting business logic. Outgoing data is serialized via response DTOs (`UserResponse`, `ExpenseResponse`), ensuring sensitive fields (like password hashes) are never accidentally exposed.
*   **Singleton Pattern (Database Engine)**: The SQLAlchemy `async_engine` and session factory (`AsyncSessionLocal`) will be instantiated once at application startup and shared across the application to manage connection pooling efficiently.
*   **Single Responsibility Principle (SRP) / Service Layer Pattern**: Frontend API calls are abstracted into a dedicated `api.js` service layer, rather than scattering `fetch` calls throughout UI components.
*   **Strategy / Adapter Pattern (AI Integration)**: For interacting with different AI providers (e.g., OpenAI, Gemini), a Strategy or Adapter pattern will be used to allow easily swapping out the underlying AI engine without altering the core business logic. See [`docs/AGENTIC_AI_SETUP.md`](../docs/AGENTIC_AI_SETUP.md).

## 2. Database Schema (Entity Relationship)

The core data models are defined in [`backend/app/models.py`](../backend/app/models.py) using SQLAlchemy declarative base from [`backend/app/database.py`](../backend/app/database.py). Validation schemas live in [`backend/app/schemas.py`](../backend/app/schemas.py).

### 2.1 `User` Entity
*   `id` (Integer, Primary Key)
*   `email` (String, Unique, Indexed)
*   `username` (String, Unique, Indexed)
*   `hashed_password` (String) - Bcrypt hashed, implemented in [`backend/app/auth.py`](../backend/app/auth.py)
*   `full_name` (String, Nullable)
*   `is_active` (Boolean, Default: True)
*   `is_verified` (Boolean, Default: False) - Email OTP verification
*   `otp_code` (String, Nullable) - One-time password for email verification
*   `otp_expires_at` (DateTime, Nullable)
*   `role` (String, Default: "free") - RBAC tier: `free`, `pro`, `enterprise`, `admin`. See [`docs/RBAC.md`](../docs/RBAC.md)
*   `features_enabled` - Computed `@property` (not a DB column) that derives feature access from `role`
*   `refresh_token` (String, Nullable) - For persistent login session management
*   `token_expires_at` (DateTime, Nullable)
*   `failed_login_attempts` (Integer, Default: 0) - Brute-force protection
*   `locked_until` (DateTime, Nullable) - Account lockout timestamp
*   `created_at` (DateTime)
*   `updated_at` (DateTime)

### 2.2 `Category` Entity
*   `id` (Integer, Primary Key)
*   `name` (String, Indexed)
*   `color` (String, Nullable) - For UI display
*   `icon` (String, Nullable) - For UI display
*   `user_id` (Integer, FK to `users.id`, Nullable) - Null means a global/default category
*   `created_at` (DateTime)
*   `updated_at` (DateTime)

### 2.3 `Expense` Entity
*   `id` (Integer, Primary Key)
*   `user_id` (Integer, Foreign Key to `users.id`)
*   `category_id` (Integer, Foreign Key to `categories.id`, Nullable)
*   `amount` (Float)
*   `description` (Text, Nullable)
*   `receipt_image_url` (String, Nullable) - *Planned for AI Receipt Scanning*
*   `ai_metadata` (JSON, Nullable) - *Planned: Stores AI confidence scores and raw extracted data*
*   `created_at` (DateTime)
*   `updated_at` (DateTime)

**Relationships**:
- A `User` has a one-to-many relationship with `Expense` and `Category`. Deleting a user cascades and deletes associated expenses and categories.
- A `Category` has a one-to-many relationship with `Expense`.

## 3. API Specification (Implemented Endpoints)

Routes are organized using `APIRouter` in [`backend/app/routers/`](../backend/app/routers/).

### 3.1 Authentication ([`auth_routes.py`](../backend/app/routers/auth_routes.py))
*   `POST /auth/register` - Create a new user account, block disposable emails, send OTP.
*   `POST /auth/verify-otp` - Verify email OTP and return access + refresh tokens.
*   `POST /auth/login` - Authenticate user and return JWT access + refresh tokens.
*   `POST /auth/refresh` - Renew access token using HttpOnly refresh cookie.
*   `POST /auth/logout` - Revoke refresh token and clear cookie.
*   `GET /auth/me` - Return current user's profile (protected).

### 3.2 Users ([`user_routes.py`](../backend/app/routers/user_routes.py))
*   `GET /users` - List all users (admin only).
*   `GET /users/{user_id}` - Retrieve a specific user by ID.
*   `PUT /admin/users/{id}/features` - *(Admin only)* Update user feature flags.

### 3.3 Expenses ([`expense_routes.py`](../backend/app/routers/expense_routes.py))
*   `GET /expenses` - Retrieve a list of expenses for the authenticated user. Supports filtering.
*   `POST /expenses` - Create a new expense record.
*   `GET /expenses/{id}` - Retrieve a specific expense by ID.
*   `PUT /expenses/{id}` - Update a specific expense.
*   `DELETE /expenses/{id}` - Delete a specific expense.

### 3.4 Categories ([`category_routes.py`](../backend/app/routers/category_routes.py))
*   `POST /categories` - Create a custom category.
*   `GET /categories` - List user's categories.
*   `DELETE /categories/{id}` - Delete a category.

### 3.5 Health & System
*   `GET /health` - API health check.
*   `GET /health/db` - Database connection health check.

### 3.6 Planned Endpoints
*   `POST /expenses/scan-receipt` - Upload a receipt image for OCR processing.
*   `POST /expenses/categorize` - AI-suggested category from description.
*   `GET /analytics/insights` - LLM-generated spending insights.
*   `POST /ai/chat` - Multi-agent AI advisor (REST or WebSocket).
*   `GET /admin/feature-flags` - Active feature flags for the environment.

## 4. Frontend Component Architecture

The React frontend will be structured around functional components and hooks:

*   **State Management**: React `useState` and `useEffect` for local component state. Consider React Context (e.g., `FeatureFlagProvider`) or a lightweight library (Zustand) if global state (e.g., authenticated user data, feature flags) becomes complex.
*   **Routing**: React Router for navigating between `/dashboard`, `/expenses/add`, and `/profile`.
*   **Service Layer ([`src/services/api.js`](../frontend/src/services/api.js))**: Encapsulates all network requests. Functions like `getExpenses()`, `createExpense(data)`, `scanReceipt(image)`, and `getInsights()` will handle headers, authentication tokens, and error parsing.
*   **UI Components**: Reusable Tailwind-styled components (e.g., `Button`, `InputField`, `ExpenseCard`, `StatusIndicator`). See [`frontend/src/components/`](../frontend/src/components/).

## 5. Security & Validation specifics

*   **Pydantic Validation**: All endpoints will use Pydantic to enforce data types, string lengths, and required fields before processing.
*   **Password Hashing**: The `passlib` library with `bcrypt` is used to hash passwords on registration and verify them on login. See [`backend/app/auth.py`](../backend/app/auth.py).
*   **JWT Security**: Access tokens are short-lived (15 min). Refresh tokens are stored in HttpOnly cookies. The FastAPI dependency `OAuth2PasswordBearer` extracts and validates the token from the `Authorization: Bearer <token>` header for protected routes. See [Security Checklist](security-checklist.md) for the full requirements.

---

## 🔗 See Also

- [High-Level Design](high-level-design.md) — System architecture and requirements
- [Security Checklist](security-checklist.md) — OWASP ASVS deployment hardening
- [TODO.md](../TODO.md) — Development roadmap
- [PROJECT_STATE.md](../PROJECT_STATE.md) — Current project state and DB schema
- [RBAC](../docs/RBAC.md) — Role-Based Access Control tiers
- [Agentic AI Setup](../docs/AGENTIC_AI_SETUP.md) — AI implementation guide
