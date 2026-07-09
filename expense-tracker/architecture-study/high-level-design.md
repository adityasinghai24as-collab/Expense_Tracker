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
*   **AI-Powered Features**: *(Note: These features are currently in Beta and controlled via feature flags. They may not be visible to all users.)*
    *   **Receipt Scanning**: Users can upload receipt images for automatic data extraction (amount, date, description).
    *   **Smart Categorization**: The system automatically suggests expense categories based on descriptions.
    *   **Spending Insights**: Generates natural language insights about user spending habits.

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

### 3.4 External Services (AI Integration)
*   **Provider**: External AI Models (e.g., OpenAI, Google Gemini, AWS Textract).
*   **Responsibilities**: 
    *   Process receipt images for OCR and structured data extraction.
    *   Analyze text for automatic expense categorization.
    *   Provide natural language analysis of user spending data.

## 4. Planned Components & Services

1.  **Web Client**: The browser-based interface accessed by the user.
2.  **API Gateway / Reverse Proxy**: Routes requests to the appropriate backend services (handled by Vite proxy in dev, and a reverse proxy/Ingress in production).
3.  **Auth Service (Logical)**: Handles token generation, validation, and user session management within the FastAPI application.
4.  **Expense Service (Logical)**: Contains the core business logic for managing financial records.
5.  **PostgreSQL Database**: The relational data store.
6.  **AI Integration Service**: Handles communication with external LLM and Vision APIs to process unstructured data (images, text) into structured expense data and insights.
7.  **Feature Flag Service (Logical)**: Manages and resolves the state of feature flags for users, controlling access to new capabilities like AI features via a JSON column in the database.

## 5. Deployment Architecture
*   **Containerization**: Both the Backend and Frontend will be containerized using Docker.
*   **Development**: Orchestrated using Docker Compose to spin up the API and Database simultaneously.
*   **Production**: The Backend Docker image will be deployed to Google Cloud Run. The database will be a managed PostgreSQL instance on Neon. The frontend static assets will be served via a CDN (e.g., Cloudflare Pages, Vercel, or Firebase Hosting).
