terraform {
  required_version = ">= 1.5.0"

  backend "gcs" {
    bucket = "expense-tracker-tf-state" # Change this to your unique bucket name
    # prefix is set at `terraform init` time via:
    #   terraform init -backend-config="prefix=terraform/state/<ENV>"
    # This isolates state per environment (dev, staging, prod).
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    neon = {
      source  = "kislerdm/neon"
      version = "~> 0.2"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "neon" {
  api_key = var.neon_api_key
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}
