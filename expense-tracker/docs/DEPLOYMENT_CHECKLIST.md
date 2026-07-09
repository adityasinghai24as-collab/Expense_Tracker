# Deployment Checklist

Use this checklist every time you deploy to **any** environment. Copy this section and fill it out for auditing purposes.

---

## 🔑 Legend

| Environment | Branch | Terraform Var File | Approval Required |
|---|---|---|---|
| `dev` | `develop` | `environments/dev.tfvars` | No |
| `staging` | `staging` | `environments/staging.tfvars` | No |
| `prod` | `main` | `environments/prod.tfvars` | **Yes** (manual gate) |

---

## Pre-Deployment

- [ ] **Target Environment**: ____________ (`dev` / `staging` / `prod`)
- [ ] **Deploying Commit**: ____________ (git SHA)
- [ ] All unit tests pass (`pytest` backend, `vitest` frontend)
- [ ] Code quality scan is green (Ruff, ESLint, SonarQube)
- [ ] Security scan is green (Trivy — no CRITICAL/HIGH vulnerabilities)
- [ ] Feature flags in `environments/<env>.tfvars` are correct for this release
- [ ] Database migrations (if any) have been tested locally
- [ ] For **production only**: PR has been reviewed and merged into `main`

## Deployment Steps

### Option A: Jenkins (Automated — Recommended)

1. Go to your Jenkins Dashboard → **Expense-Tracker-Pipeline**.
2. Click **Build with Parameters**.
3. Select the `DEPLOY_ENV` parameter:
   - `dev` for development
   - `staging` for staging
   - `prod` for production
4. Click **Build**.
5. For **production**: approve the manual gate when prompted.
6. Wait for all stages to turn green.

### Option B: Manual Terraform

```bash
cd expense-tracker/infrastructure

# Initialize with environment-specific state
terraform init -backend-config="prefix=terraform/state/<ENV>"

# Plan — review what will change
terraform plan -var-file=environments/<ENV>.tfvars

# Apply
terraform apply -var-file=environments/<ENV>.tfvars
```

Replace `<ENV>` with `dev`, `staging`, or `prod`.

## Post-Deployment Verification

- [ ] **Health Check**: `curl https://<cloud-run-url>/health` returns `{"status": "ok"}`
- [ ] **DB Health Check**: `curl https://<cloud-run-url>/health/db` returns `{"status": "ok", "database": "postgresql"}`
- [ ] **Feature Flags**: `curl https://<cloud-run-url>/admin/feature-flags` returns expected flags for the environment
- [ ] **Frontend**: Cloudflare Pages deployment is live and connects to the correct API URL
- [ ] **Smoke Test**: Log in, create an expense, verify it appears in the list
- [ ] For **production only**: Monitor error rates and latency for 15 minutes after deploy

## Rollback Procedure

If the deployment is unhealthy:

### Quick Rollback (Cloud Run)
```bash
# List previous revisions
gcloud run revisions list --service expense-tracker-api-<ENV> --region us-central1

# Route traffic back to the previous revision
gcloud run services update-traffic expense-tracker-api-<ENV> \
  --to-revisions=<PREVIOUS_REVISION>=100 \
  --region us-central1
```

### Full Rollback (Terraform)
```bash
# Revert to the previous commit
git revert HEAD

# Re-apply with the reverted code
terraform apply -var-file=environments/<ENV>.tfvars
```

## Sign-Off

- [ ] Deployment verified by: ____________
- [ ] Date/Time: ____________
- [ ] Notes: ____________
