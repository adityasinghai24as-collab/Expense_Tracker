# ---------------------------------------------------------
# Neon Database (Environment-scoped)
# ---------------------------------------------------------

resource "neon_project" "expense_tracker_db" {
  name                      = "expense-tracker-${var.environment}"
  history_retention_seconds = 86400
}

resource "neon_branch" "main" {
  project_id = neon_project.expense_tracker_db.id
  name       = var.environment
}

resource "neon_role" "db_user" {
  project_id = neon_project.expense_tracker_db.id
  branch_id  = neon_branch.main.id
  name       = "expense_admin"
}

resource "neon_database" "expense_db" {
  project_id = neon_project.expense_tracker_db.id
  branch_id  = neon_branch.main.id
  name       = "expensedb"
  owner_name = neon_role.db_user.name
}

resource "neon_endpoint" "main" {
  project_id = neon_project.expense_tracker_db.id
  branch_id  = neon_branch.main.id
}

# ---------------------------------------------------------
# Google Cloud Run — Backend (Environment-scoped)
# ---------------------------------------------------------

resource "google_cloud_run_v2_service" "backend_api" {
  name     = "expense-tracker-api-${var.environment}"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.docker_image

      ports {
        container_port = 8000
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql://${neon_role.db_user.name}:${neon_role.db_user.password}@${neon_endpoint.main.host}/expensedb?sslmode=require"
      }

      env {
        name  = "SECRET_KEY"
        value = var.secret_key
      }

      env {
        name  = "ALGORITHM"
        value = "HS256"
      }

      env {
        name  = "APP_ENV"
        value = var.environment
      }

      env {
        name  = "FEATURE_FLAGS"
        value = jsonencode(var.feature_flags)
      }
    }
  }
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_v2_service.backend_api.location
  project     = google_cloud_run_v2_service.backend_api.project
  service     = google_cloud_run_v2_service.backend_api.name
  policy_data = data.google_iam_policy.noauth.policy_data
}

# ---------------------------------------------------------
# Cloudflare Pages — Frontend (Environment-scoped)
# ---------------------------------------------------------

resource "cloudflare_pages_project" "frontend" {
  account_id        = var.cloudflare_account_id
  name              = "expense-tracker-ui-${var.environment}"
  production_branch = var.environment == "prod" ? "main" : var.environment == "staging" ? "staging" : "develop"

  source {
    type = "github"
    config {
      owner                          = split("/", var.github_repo)[0]
      repo_name                      = split("/", var.github_repo)[1]
      production_branch              = var.environment == "prod" ? "main" : var.environment == "staging" ? "staging" : "develop"
      pr_comments_enabled            = true
      deployments_enabled            = true
      production_deployments_enabled = true
    }
  }

  build_config {
    build_command   = "npm run build"
    destination_dir = "frontend/dist"
    root_dir        = "expense-tracker"
  }

  deployment_configs {
    production {
      environment_variables = {
        VITE_API_URL = google_cloud_run_v2_service.backend_api.uri
        VITE_APP_ENV = var.environment
      }
    }
  }
}
