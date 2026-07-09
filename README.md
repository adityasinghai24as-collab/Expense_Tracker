# Expense Tracker - Educational Monorepo

Welcome to the **Expense Tracker** project! This is a full-stack learning project designed to help you explore modern web development, cloud-native infrastructure, and enterprise-grade CI/CD — tailored for developers transitioning into software architecture roles.

## 🚀 What is this project?

The Expense Tracker allows users to sign up, log their daily expenses, categorize them, and track their spending habits over time. Behind the scenes, it demonstrates best practices in project scaffolding, dependency injection, containerization, infrastructure-as-code, and full-stack integration.

*(Note: Advanced AI features like Receipt Scanning and Smart Categorization are controlled via **feature flags** and can be toggled per environment.)*

### Core Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (Async ORM) |
| **Database** | PostgreSQL 15 (Local Docker) / Neon (Cloud) |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Infrastructure** | Terraform (GCP Cloud Run + Neon + Cloudflare Pages) |
| **CI/CD** | Jenkins (Declarative Pipeline) |
| **Code Quality** | SonarQube, Ruff (Python), ESLint (JS) |
| **Security** | Trivy (vulnerability scanning), OWASP ASVS L2 |

## 📁 Repository Structure

```text
expense-tracker/
├── backend/                 # FastAPI Application
│   ├── app/                 # Core logic (routers, models, schemas, feature_flags)
│   ├── config/              # Environment variables & configurations
│   ├── scripts/             # Utility scripts for local setup
│   ├── main.py              # Application Entry Point
│   └── Dockerfile           # Optimized multi-stage build image
├── frontend/                # React Frontend Application
│   ├── src/                 # Components, pages, and hooks
│   ├── index.html           # Vite entry point
│   └── package.json
├── infrastructure/          # Terraform IaC
│   ├── environments/        # Per-environment variable files
│   │   ├── dev.tfvars
│   │   ├── staging.tfvars
│   │   └── prod.tfvars
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf
│   └── outputs.tf
├── docs/                    # Documentation
│   ├── TERRAFORM_SETUP.md
│   ├── JENKINS_SETUP.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── DOCKER_SETUP.md
│   └── DOCKER_QUICK_REF.md
├── docker-compose.yml       # Local services orchestrator
├── Jenkinsfile              # CI/CD Pipeline definition
├── sonar-project.properties # SonarQube configuration
└── PROJECT_STATE.md         # Source of truth for project status
```

## 🛠️ Getting Started (Local Setup)

The easiest way to get the project up and running is through Docker.

### Prerequisites
*   Docker & Docker Compose installed
*   (Optional) Python 3.11+ and Node.js 18+ for non-Docker development

### 1. The "One-Click" Docker Startup
Navigate to the `expense-tracker` directory and start the services:

```bash
cd expense-tracker
docker compose up -d
```
*   **Backend API** will be running at: `http://localhost:8000` (Swagger UI at `/docs`)
*   **Database** will be listening on port `5432`

### 2. Frontend Local Development
To work on the frontend interactively with Hot-Module Replacement (HMR):

```bash
cd expense-tracker/frontend
npm install
npm run dev
```
*   **Frontend UI** will be available at: `http://localhost:5173`

## 🌍 Deployment

### Environments

The project supports three isolated environments, each with its own database, backend service, and frontend deployment:

| Environment | Branch | Purpose |
|---|---|---|
| **Development** | `develop` | Day-to-day development, all feature flags ON |
| **Staging** | `staging` | QA and pre-production validation |
| **Production** | `main` | Live users, only stable features enabled |

### Automated Deployment (CI/CD)

Deployments are fully automated via a **Jenkins Pipeline** (`Jenkinsfile`) that runs:
1. Code Quality checks (Ruff, ESLint, SonarQube)
2. Security Scans (Trivy)
3. Unit Tests (Pytest, Vitest)
4. Docker Build & Push to Google Artifact Registry
5. Terraform Apply to provision/update Cloud Run, Neon, and Cloudflare Pages
6. Post-deploy Smoke Tests

Production deployments require a **manual approval gate**.

📖 **Setup Guides:**
*   [Terraform Setup Guide](expense-tracker/docs/TERRAFORM_SETUP.md)
*   [Jenkins Setup Guide](expense-tracker/docs/JENKINS_SETUP.md)
*   [Deployment Checklist](expense-tracker/docs/DEPLOYMENT_CHECKLIST.md)

### Feature Flags

Feature availability is controlled per-environment via a `FEATURE_FLAGS` JSON env var injected by Terraform:

| Flag | Dev | Staging | Prod |
|---|---|---|---|
| `enable_receipt_scanning` | ✅ | ✅ | ❌ |
| `enable_smart_categorization` | ✅ | ✅ | ❌ |
| `enable_debug_mode` | ✅ | ❌ | ❌ |
| `enable_rate_limiting` | ❌ | ✅ | ✅ |

Flags are configured in `infrastructure/environments/<env>.tfvars` and can be inspected at runtime via `GET /admin/feature-flags`.

## 🧠 Educational Goals

Throughout the codebase, you will find `TODO: SDE-2 Task X` comments. These are intentional!
Parts of the database connection logic, frontend data fetching, and more advanced architectural pieces have been left blank to serve as practical learning exercises.

Your goal is to follow the hints, complete the tasks, and successfully connect the entire stack!

## 📌 Project Tracking
Please refer to the `PROJECT_STATE.md` file for an in-depth view of the database schema, environment variable setup, architectural overview, and the priority list of pending tasks.
