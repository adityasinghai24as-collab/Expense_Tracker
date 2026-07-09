# Development Environment
environment = "dev"

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
secret_key  = "dev-secret-key-change-me"

# Feature Flags — all experimental features ON in dev
feature_flags = {
  enable_receipt_scanning       = true
  enable_smart_categorization   = true
  enable_debug_mode             = true
  enable_rate_limiting          = false
}
