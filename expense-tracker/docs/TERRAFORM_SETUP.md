# Terraform Setup Guide

This guide explains how to use the Infrastructure as Code (IaC) configuration located in the `infrastructure/` directory to deploy the complete Expense Tracker stack across multiple environments.

The stack includes:
1. **Neon**: Serverless PostgreSQL Database.
2. **Google Cloud Run**: Serverless Backend API (FastAPI).
3. **Cloudflare Pages**: Static Frontend Hosting (React + Vite).

Each environment (dev, staging, prod) gets its own isolated set of resources.

## Prerequisites

1. Install [Terraform](https://developer.hashicorp.com/terraform/downloads) (version >= 1.5.0).
2. Install the [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) and run `gcloud auth application-default login`.
3. Create accounts on [Google Cloud](https://cloud.google.com/), [Neon](https://neon.tech/), and [Cloudflare](https://www.cloudflare.com/).

## Step 1: Obtain API Credentials

### Neon
1. Go to your Neon Dashboard > Account Settings > Developer Settings.
2. Generate a new **API Key**.

### Cloudflare
1. Go to your Cloudflare Dashboard > My Profile > API Tokens.
2. Create an API token with permissions to edit Cloudflare Pages.
3. Note your **Account ID** from the main dashboard (right sidebar).

### Google Cloud
1. Create a new Google Cloud Project.
2. Note your **Project ID**.
3. Enable the following APIs in the Cloud Console:
   - Cloud Run API
   - Secret Manager API
4. Create a GCS bucket for Terraform state:
   ```bash
   gsutil mb -p YOUR_PROJECT_ID gs://expense-tracker-tf-state
   ```

## Step 2: Configure Per-Environment Variables

We use **separate variable files** for each environment instead of a single `terraform.tfvars`. These live in `infrastructure/environments/`:

| File | Environment | Git Branch |
|---|---|---|
| `environments/dev.tfvars` | Development | `develop` |
| `environments/staging.tfvars` | Staging | `staging` |
| `environments/prod.tfvars` | Production | `main` |

Edit each file with your API keys and environment-specific settings. The `feature_flags` map controls which features are enabled per environment.

## Step 3: Initialize Terraform (Per Environment)

Each environment has its own **isolated state file** in GCS. You must pass the state prefix at init time:

```bash
cd infrastructure

# For development:
terraform init -backend-config="prefix=terraform/state/dev"

# For staging:
terraform init -backend-config="prefix=terraform/state/staging"

# For production:
terraform init -backend-config="prefix=terraform/state/prod"
```

> **Important**: If you switch between environments, you must re-run `terraform init` with the new prefix. Terraform will prompt you to confirm.

## Step 4: Plan the Deployment

```bash
# Development
terraform plan -var-file=environments/dev.tfvars

# Staging
terraform plan -var-file=environments/staging.tfvars

# Production
terraform plan -var-file=environments/prod.tfvars
```

Review the output to ensure the correct environment-specific resources will be created (e.g., `expense-tracker-api-dev`, `expense-tracker-api-staging`).

## Step 5: Apply

```bash
terraform apply -var-file=environments/dev.tfvars
```

Type `yes` when prompted.

Once complete, Terraform will output:
* `environment`: The deployed environment name.
* `backend_url`: The URL of your live API.
* `frontend_url`: The URL of your live frontend UI.
* `feature_flags`: The active feature flags for this environment.

## CI/CD Pipeline Configuration (Jenkins)

In practice, you will rarely run `terraform apply` manually. The Jenkins pipeline handles this automatically:

- Pushes to `develop` → deploy to **dev**
- Pushes to `staging` → deploy to **staging**
- Pushes to `main` → deploy to **prod** (with manual approval gate)

To set up the pipeline, see the **[Jenkins Setup Guide](JENKINS_SETUP.md)**.

For a step-by-step deployment procedure, see the **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)**.

---

## 🔗 See Also

- [Jenkins Setup Guide](JENKINS_SETUP.md) — CI/CD pipeline automation
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) — Pre/post-deploy verification
- [TODO.md](../TODO.md) — Phase 7 (Deployment tasks)
- **Key code/config files**: [`infrastructure/main.tf`](../infrastructure/main.tf), [`infrastructure/variables.tf`](../infrastructure/variables.tf), [`infrastructure/providers.tf`](../infrastructure/providers.tf), [`infrastructure/outputs.tf`](../infrastructure/outputs.tf), [`infrastructure/environments/`](../infrastructure/environments/)
