# Staging Environment
environment = "staging"

# GCP
gcp_project_id = "your-gcp-project-id"
gcp_region     = "us-central1"

# Docker
docker_image = "gcr.io/your-gcp-project-id/expense-backend:latest"

# Neon
neon_api_key = "your-neon-api-key"

# Cloudflare
cloudflare_api_token  = "your-cloudflare-api-token"
cloudflare_account_id = "your-cloudflare-account-id"

# App
github_repo = "your-username/expense-tracker"
secret_key  = "staging-secret-key-change-me"

# Feature Flags — experimental features ON for QA, debug OFF
feature_flags = {
  enable_receipt_scanning       = true
  enable_smart_categorization   = true
  enable_debug_mode             = false
  enable_rate_limiting          = true
}
