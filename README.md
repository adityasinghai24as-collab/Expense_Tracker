# Expense Tracker - Full-Stack Enterprise Monorepo

Welcome to the **Expense Tracker** project! This is a production-grade full-stack application demonstrating modern web development, cloud-native infrastructure, and enterprise-grade CI/CD — built with enterprise architectural standards.

## 🚀 What is this project?

The Expense Tracker allows users to sign up, log their daily expenses, categorize them, and track their spending habits over time. Behind the scenes, it demonstrates best practices in project scaffolding, dependency injection, containerization, infrastructure-as-code, and full-stack integration.

*(Note: Advanced features like the **Autonomous Multi-Agent Financial Advisor**, **Local RAG**, and **Human-in-the-Loop Safety** are controlled via **LaunchDarkly**. This enterprise-grade feature management system enables local evaluation, backend kill switches, and targeted canary releases per environment.)*

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
│   ├── ai/                  # Multi-Agent LangGraph Orchestrator (State, Tools, Graph)
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
│   ├── DOCKER_QUICK_REF.md
│   └── AGENTIC_AI_SETUP.md  # Setup guide for local RAG & LangGraph
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

### LaunchDarkly Feature Management

This project uses **LaunchDarkly** for robust feature flag management instead of static environment variables. This enables:
*   **Backend Kill Switches**: Instantly pause sensitive operations (e.g., executing transactions or AI actions) without deploying code.
*   **Local Evaluation**: The FastAPI backend initializes a LaunchDarkly Server-Side SDK singleton to cache rulesets locally, ensuring zero-latency flag evaluations.
*   **Canary Releases**: The React frontend uses dynamic Context updates to gradually roll out features to specific user tiers (Free vs Pro).

**Local Development Strategy**: To prevent hitting production flags during local development, developers use the LaunchDarkly `TestData` mock source or the fallback `.env` defaults, as outlined in the [LaunchDarkly Setup Guide](expense-tracker/docs/launchdarkly-integration-guide.md).

| Flag Pattern | Purpose |
|---|---|
| `feat-*` | New functionality rollouts (e.g., `feat-receipt-scanning`) |
| `kill-*` | Operational kill switches (e.g., `kill-order-execution`) |

Flags can be inspected at runtime via `GET /admin/feature-flags` (Admin only).

## 🧠 Architecture & Task Roadmap

Throughout the codebase, you will find `TODO: Task X` comments outlining structured architecture tasks and feature enhancements.

Refer to `TODO.md` and `PROJECT_STATE.md` for a comprehensive list of task priorities, implementation status, and architectural milestones across the stack.

## 📌 Project Tracking
Please refer to the `PROJECT_STATE.md` file for an in-depth view of the database schema, environment variable setup, architectural overview, and the priority list of pending tasks.
