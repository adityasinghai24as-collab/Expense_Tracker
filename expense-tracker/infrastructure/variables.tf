variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "gcp_project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "gcp_region" {
  description = "Google Cloud Region for Cloud Run"
  type        = string
  default     = "us-central1"
}

variable "neon_api_key" {
  description = "Neon API Key"
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "Cloudflare API Token"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare Account ID"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository for Cloudflare Pages (e.g. your-username/expense-tracker)"
  type        = string
}

variable "docker_image" {
  description = "Docker image for Cloud Run (e.g. gcr.io/your-project/expense-backend:latest)"
  type        = string
}

variable "secret_key" {
  description = "Backend Secret Key"
  type        = string
  sensitive   = true
}

variable "feature_flags" {
  description = "Feature flags map injected into the backend container"
  type        = map(bool)
  default = {
    enable_receipt_scanning     = false
    enable_smart_categorization = false
    enable_debug_mode           = true
    enable_rate_limiting        = false
  }
}
