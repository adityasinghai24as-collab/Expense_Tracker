# Jenkins CI/CD Setup Guide

This project uses a **Declarative Jenkins Pipeline** ([`Jenkinsfile`](../Jenkinsfile)) to automate Code Quality, Security Scanning, Unit Testing, and multi-environment Infrastructure Deployment via Terraform.

## Pipeline Architecture

The pipeline runs 8 stages in order:

| Stage | Description | Runs On |
|---|---|---|
| **Resolve Environment** | Auto-detects target env from branch | All branches |
| **Checkout** | Pulls code from SCM | All branches |
| **Code Quality** | Ruff, ESLint, SonarQube | All branches |
| **Security Scans** | Trivy vulnerability scanner | All branches |
| **Unit Tests** | Pytest (backend), Vitest (frontend) | All branches |
| **Build & Push** | Docker build → Artifact Registry | `develop`, `staging`, `main` |
| **Production Approval** | Manual gate (human must click "Yes") | `main` only |
| **Deploy Infrastructure** | `terraform apply` with env-specific vars | `develop`, `staging`, `main` |
| **Smoke Test** | Health check + feature flags verification | `develop`, `staging`, `main` |

### Branch → Environment Mapping

| Branch | Environment | Terraform Vars | Approval |
|---|---|---|---|
| `develop` | dev | `environments/dev.tfvars` | No |
| `staging` | staging | `environments/staging.tfvars` | No |
| `main` | prod | `environments/prod.tfvars` | **Yes** |

## Running Jenkins Locally (Docker)

The fastest way to get Jenkins running is via the provided Docker Compose setup. This builds a custom Jenkins image with **all pipeline tools pre-installed** (Docker CLI, Terraform, Node.js, Python, Trivy, gcloud, SonarQube Scanner) and also starts a local SonarQube instance.

### Quick Start

```bash
# From the repository root
docker compose -f docker-compose.jenkins.yml up -d --build
```

| Service | URL | Default Credentials |
|---|---|---|
| **Jenkins** | http://localhost:8080 | Setup wizard is disabled; configure admin on first boot |
| **SonarQube** | http://localhost:9000 | `admin` / `admin` |

### What's Included

The custom `jenkins.Dockerfile` pre-installs:
- Docker CLI (uses host Docker socket for builds)
- Node.js 18 & npm
- Python 3 & Ruff
- Terraform 1.5.7
- Trivy (vulnerability scanner)
- Google Cloud CLI (`gcloud`)
- SonarQube Scanner CLI
- All required Jenkins plugins (Pipeline, Credentials Binding, SonarQube, Blue Ocean, etc.)

### First-Time Setup

1. Open http://localhost:8080 and create your admin user.
2. Go to **Manage Jenkins > System > SonarQube servers** and add:
   - **Name**: `SonarQubeServer`
   - **URL**: `http://sonarqube:9000` (uses the Docker network hostname)
   - **Token**: Generate one from http://localhost:9000 > My Account > Security
3. Follow the credential configuration in **Step 1** below.

### Stopping Jenkins

```bash
docker compose -f docker-compose.jenkins.yml down
```

Data is persisted in Docker volumes (`jenkins-home-data`, `sonarqube-data`), so your configuration survives restarts.

---

## Prerequisites for your Jenkins Server

> **Note**: If you are using the Docker setup above, all tools are already pre-installed. This section is for self-managed Jenkins servers.

Your Jenkins instance needs the following tools installed (either globally or via Jenkins Global Tool Configuration):
1. **Docker**: To build and push images.
2. **Terraform** (>= 1.5.0): To provision the infrastructure.
3. **Python 3.11+ & pip**: To run backend linting (`ruff`) and tests (`pytest`).
4. **Node.js 18+ & npm**: To run frontend linting (`eslint`) and tests (`vitest`).
5. **Trivy**: To scan for vulnerabilities.
6. **Google Cloud CLI (`gcloud`)**: To authenticate with GCP.

### Required Jenkins Plugins
Ensure the following plugins are installed via **Manage Jenkins > Plugins**:
- **Pipeline** (Usually installed by default)
- **Credentials Binding Plugin**
- **SonarQube Scanner for Jenkins**
- **Docker Pipeline** (optional, for Docker-based agents)

## Step 1: Configure Credentials in Jenkins

The `Jenkinsfile` relies on several credentials. You must add these in **Manage Jenkins > Credentials > System > Global credentials**.

| Credential ID | Type | Description |
|---|---|---|
| `gcp-project-id` | Secret text | Your Google Cloud Project ID. |
| `gcp-credentials` | Secret file | The JSON key file for a GCP Service Account with Cloud Run and Artifact Registry permissions. |
| `neon-api-key` | Secret text | Your Neon Developer API Key. |
| `cloudflare-api-token` | Secret text | Your Cloudflare API Token. |
| `cloudflare-account-id` | Secret text | Your Cloudflare Account ID. |
| `backend-secret-key` | Secret text | A secure random string used by FastAPI for JWT encryption. |

## Step 2: Configure SonarQube in Jenkins

1. Go to **Manage Jenkins > System**.
2. Scroll to **SonarQube servers**.
3. Click **Add SonarQube**.
4. Name it exactly: `SonarQubeServer` (this matches the `withSonarQubeEnv('SonarQubeServer')` block in the `Jenkinsfile`).
5. Provide your SonarQube server URL and a Server authentication token.

## Step 3: Create the Pipeline Job

1. On the Jenkins dashboard, click **New Item**.
2. Enter a name for the job (e.g., `Expense-Tracker-Pipeline`).
3. Select **Multibranch Pipeline** and click **OK**.
4. Under **Branch Sources**, add your Git repository.
5. Configure branch discovery to include `develop`, `staging`, and `main`.
6. Jenkins will auto-discover the `Jenkinsfile` in each branch.

> **Why Multibranch?** This allows Jenkins to auto-create a pipeline for each branch. The `Jenkinsfile` auto-detects the environment from the branch name (`develop`→dev, `staging`→staging, `main`→prod), so a single pipeline definition handles all environments.

## Step 4: Manual Builds (Optional)

If you want to deploy a specific environment manually (e.g., re-deploy dev from the `develop` branch):

1. Go to the `develop` branch pipeline.
2. Click **Build with Parameters**.
3. Select `DEPLOY_ENV` = `dev`.
4. Click **Build**.

## Step 5: Verify

After a successful build, check the Terraform outputs in the Jenkins console log:
- `environment`: Should match `dev`, `staging`, or `prod`.
- `backend_url`: The live API URL.
- `frontend_url`: The live frontend URL.
- `feature_flags`: The active flags for this environment.

The pipeline also runs a post-deploy **Smoke Test** that verifies the `/health`, `/health/db`, and `/admin/feature-flags` endpoints.

For a comprehensive pre/post deployment procedure, see the **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)**.

---

## 🔗 See Also

- [Terraform Setup Guide](TERRAFORM_SETUP.md) — Infrastructure as Code deployment
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) — Pre/post-deploy steps and rollback
- [Security Checklist](../architecture-study/security-checklist.md) — Production hardening (§ CI/CD Security)
- [TODO.md](../TODO.md) — Phase 9 (CI/CD Pipeline tasks)
- **Key code/config files**: [`Jenkinsfile`](../Jenkinsfile), [`sonar-project.properties`](../sonar-project.properties)
