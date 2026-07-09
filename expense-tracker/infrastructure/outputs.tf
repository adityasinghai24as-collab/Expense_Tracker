output "environment" {
  description = "The deployed environment"
  value       = var.environment
}

output "backend_url" {
  description = "The public URL of the Google Cloud Run API"
  value       = google_cloud_run_v2_service.backend_api.uri
}

output "frontend_url" {
  description = "The public URL of the Cloudflare Pages deployment"
  value       = cloudflare_pages_project.frontend.subdomain
}

output "database_project" {
  description = "The Neon project name"
  value       = neon_project.expense_tracker_db.name
}

output "feature_flags" {
  description = "Active feature flags for this environment"
  value       = var.feature_flags
}
