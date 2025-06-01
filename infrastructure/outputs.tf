output "frontend_url" {
  value = "https://storage.googleapis.com/${google_storage_bucket.frontend.name}/index.html"
}

output "api_url" {
  value = google_cloud_run_service.api.status[0].url
} 