# Expense Tracker - High Level Design (HLD)

## 1. System Overview
The Expense Tracker is a full-stack web application designed to help users manage their personal finances. Users can create accounts, log their daily expenses, categorize them, and view their spending habits over time. The system is built with a modern, containerized architecture suitable for cloud deployment.

## 2. Requirements

### 2.1 Functional Requirements
*   **User Management**: 
    *   Users must be able to register, log in, and manage their profiles.
    *   Secure authentication using JWT (JSON Web Tokens).
*   **Expense Management**:
    *   Users can add, edit, delete, and view their expenses.
    *   Each expense must include an amount, description, category, and timestamp.
*   **Categorization**:
    *   Users can assign expenses to predefined or custom categories (e.g., Food, Transport, Utilities).
*   **Analytics/Reporting**:
    *   Users can view a dashboard summarizing their total expenses, category breakdowns, and recent transactions.
*   **AI-Powered Features & Multi-Agent Orchestration**: *(Note: These features are currently in Beta and controlled via feature flags. They may not be visible to all users.)*
    *   **Autonomous Financial Advisor**: A LangGraph-powered multi-agent system (Supervisor, Analyst, Action Executor) that autonomously manages finances via natural language.
    *   **Local RAG for Financial Documents**: Chat with uploaded bank statements or tax forms using local vector databases (ChromaDB) and embeddings.
    *   **Human-in-the-Loop (HITL) Safety**: Graph execution pauses for explicit user approval via the UI before executing destructive or high-stakes actions.
    *   **Self-Healing Agents**: Agents autonomously catch, reflect on, and recover from tool execution errors.
    *   **Voice-to-Action**: Log expenses using voice via Web Speech API integration.
    *   **Receipt Scanning**: Users can upload receipt images for automatic data extraction (amount, date, merchant) using Vision APIs.
    *   **Smart Categorization**: The system automatically suggests expense categories based on descriptions.
    *   **Spending Insights**: Generates natural language insights about user spending habits using LLMs.
*   **Advanced Tracking & Multi-currency**:
    *   **Multi-Currency Support**: Log expenses in native currencies and auto-convert to a base currency (USD) using live FX rates.
    *   **Split Transactions**: Split a single receipt across multiple distinct categories.
    *   **Tags & Geolocation**: Add custom `#tags`, attach PDF invoices, and log GPS coordinates.
*   **Automation & Planning**:
    *   **Recurring Expenses**: Background cron jobs automatically generate records for subscriptions (Netflix, Rent).
    *   **Budgets & Alerts**: Users set spending limits per category. The system fires alerts when nearing limits (e.g., 90%).
*   **Multiplayer & Export**:
    *   **Shared Wallets (Groups)**: Allow roommates or couples to share an expense book with "who owes who" settlements.
    *   **Advanced Analytics & Export**: View Month-over-Month heatmaps and export full data to CSV/PDF.

### 2.2 Non-Functional Requirements
*   **Performance**: The application should load quickly and respond to API requests with minimal latency (e.g., < 200ms for standard CRUD operations). Endpoints interfacing with external AI models (like receipt scanning) should be handled gracefully, potentially using asynchronous processing to prevent blocking.
*   **Scalability & Load Testing**: The system must be capable of handling hundreds to thousands of concurrent users. Rigorous load testing must be performed to simulate peak usage scenarios, ensuring the backend and database do not degrade under high concurrency.
*   **Testing Rigor**: The application requires comprehensive unit testing for both frontend and backend to guarantee business logic correctness and avoid regressions.
*   **Enterprise Readiness**: 
    *   **Observability**: Must include structured logging, distributed tracing, and centralized error tracking.
    *   **Security**: Must implement strict RBAC, audit logging, rate limiting, and data encryption.
    *   **Resilience**: Needs high availability, caching (Redis), and asynchronous processing for background tasks.
*   **Scalability**: The backend API should be stateless to allow horizontal scaling behind a load balancer.
*   **Availability**: The system should be highly available, targeting 99.9% uptime. Database clustering and robust container orchestration (e.g., Google Cloud Run) will support this.
*   **Security**: 
    *   Passwords must be hashed (e.g., using bcrypt) before storage.
    *   All API communication must occur over HTTPS.
    *   CORS policies must be strictly enforced.
    *   **Persistent Login**: JWT access tokens (short-lived, 15 min) + refresh tokens (long-lived, 7-30 days) stored in HttpOnly cookies. Users stay logged in across browser sessions without re-entering credentials.
    *   **Security Standards**: The application targets **OWASP ASVS Level 2** compliance. See [`architecture-study/security-checklist.md`](./security-checklist.md) for the full deployment hardening checklist (OWASP ASVS / CIS Benchmarks / NIST-aligned).
*   **Maintainability**: The codebase must adhere to clean architecture principles, making it easy for new developers to onboard and add features.

## 3. Architecture Overview

The system follows a classic 3-tier architecture:

### 3.1 Presentation Tier (Frontend)
*   **Framework**: React 18, Vite
*   **Styling**: Tailwind CSS
*   **Responsibilities**: 
    *   Render the UI and handle user interactions.
    *   Manage client-side routing.
    *   Communicate with the backend API via a dedicated Service layer.
    *   Manage client-side state (e.g., using React Context or simple state hooks).

### 3.2 Application Tier (Backend API)
*   **Framework**: FastAPI (Python)
*   **AI Frameworks**: LangChain, LangGraph (for multi-agent orchestration)
*   **Server**: Uvicorn (ASGI)
*   **Responsibilities**: 
    *   Expose RESTful endpoints for the frontend.
    *   Handle business logic and data validation.
    *   Manage authentication and authorization (JWT access + refresh tokens).
    *   Interact with the database.

### 3.3 Data Tier (Database)
*   **Engine**: PostgreSQL 15
*   **Access**: SQLAlchemy (Async ORM) + asyncpg
*   **Responsibilities**: 
    *   Persistently store user data, expenses, and categories.
    *   Ensure data integrity through relational constraints (Foreign Keys).

### 3.4 External Services & APIs
*   **AI Providers**: External AI Models (e.g., OpenAI, Google Gemini, AWS Textract) for OCR receipt scanning and natural language spending insights.
*   **Financial APIs**: Exchange Rate APIs (e.g., OpenExchangeRates) to fetch live FX conversions for multi-currency transactions.
*   **LaunchDarkly**: Enterprise feature flag management service used for remote config, kill switches, and targeted feature rollouts.

### 3.5 Container Roles (Docker Compose)
The application runs locally using Docker Compose, orchestrating the following containers:
*   **`backend` (FastAPI Application)**: The core Python web server exposing REST API endpoints. It handles authentication, business logic, and orchestrates reads/writes to the database.
*   **`postgres` (PostgreSQL Database)**: Provides persistent storage (Source of Truth) for users, passwords, expense records, and categories. Connected via SQLAlchemy and the async `asyncpg` driver.
*   **`redis` (In-Memory Data Store)**: Intended for rate limiting (preventing API abuse), caching heavy database queries, and acting as a message broker for background tasks (e.g., async emails).
*   **`promtail` (Log Collector)**: Part of the PLG observability stack. It watches local log files generated by containers, attaches metadata/labels, and ships them over the network.
*   **`loki` (Log Aggregation Database)**: Receives log streams from Promtail. It efficiently indexes only the log labels and compresses the actual text, making it a highly scalable centralized log database.
*   **`grafana` (Visualization Dashboard)**: Provides a web UI to query, visualize, and set alerts on the log data stored in Loki using LogQL.

## 4. Planned Components & Services

1.  **Web Client**: The browser-based interface accessed by the user.
2.  **API Gateway / Reverse Proxy**: Routes requests to the appropriate backend services (handled by Vite proxy in dev, and a reverse proxy/Ingress in production).
3.  **Auth Service (Logical)**: Handles token generation, validation, and user session management within the FastAPI application.
4.  **Expense Service (Logical)**: Contains the core business logic for managing financial records.
5.  **PostgreSQL Database**: The relational data store.
6.  **AI Integration Service**: Handles communication with external LLM and Vision APIs to process unstructured data (images, text) into structured expense data and insights.
7.  **Multi-Agent Orchestrator (LangGraph)**: A stateful AI supervisor managing specialized sub-agents (e.g., Analyst Agent, Action Agent) capable of autonomously querying and mutating user data via LangChain tools.
8.  **Feature Flag Service (LaunchDarkly)**: Replaces the logical/JSON-based feature flags. Provides server-side local evaluation (zero-latency caching) for backend kill switches and client-side context hydration for React UI toggles.
9.  **Background Worker / Cron**: A dedicated worker process (e.g., Celery/APScheduler) for processing recurring subscriptions and generating weekly AI insights.

## 5. Deployment Architecture
*   **Containerization**: Both the Backend and Frontend will be containerized using Docker.
*   **Development**: Orchestrated using Docker Compose to spin up the API and Database simultaneously.
*   **Production**: The Backend Docker image will be deployed to Google Cloud Run. The database will be a managed PostgreSQL instance on Neon. The frontend static assets will be served via a CDN (e.g., Cloudflare Pages, Vercel, or Firebase Hosting). See [`docs/TERRAFORM_SETUP.md`](../docs/TERRAFORM_SETUP.md) for IaC details.

---

## 🔗 See Also

- [Low-Level Design](low-level-design.md) — Design patterns, DB schema, API spec
- [Security Checklist](security-checklist.md) — OWASP ASVS deployment hardening
- [TODO.md](../TODO.md) — Phase-by-phase development roadmap
- [PROJECT_STATE.md](../PROJECT_STATE.md) — Current project state and tech stack
- [User Guide](../docs/USER_GUIDE.md) — End-user feature overview
- [Agentic AI Setup](../docs/AGENTIC_AI_SETUP.md) — Multi-agent AI implementation guide
- [LaunchDarkly Guide](../docs/launchdarkly-integration-guide.md) — Feature flag management
