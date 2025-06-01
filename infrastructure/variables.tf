variable "project_id" {
  description = "The GCP project ID."
}

variable "region" {
  description = "The GCP region."
  default     = "europe-west1"
}

variable "bucket_name" {
  description = "A globally unique name for the GCS bucket."
}

variable "api_image" {
  description = "Docker image for Cloud Run (e.g., gcr.io/PROJECT_ID/word-definer-api)"
}