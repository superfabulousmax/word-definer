provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "frontend" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }
}

resource "google_storage_bucket_iam_member" "public_rule" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket_object" "frontend_files" {
  name   = each.value
  bucket = google_storage_bucket.frontend.name
  source = "${path.module}/../frontend/${each.value}"
  content_type = lookup(
    {
      "index.html" = "text/html"
      "style.css"  = "text/css"
    },
    each.value,
    "application/octet-stream"
  )
  for_each = toset(["index.html", "style.css"])
}

resource "google_cloud_run_service" "api" {
  name     = "word-definer-api"
  location = var.region

  template {
    spec {
      containers {
        image = var.api_image
        ports {
          container_port = 8000
        }
        env {
          name = "NEXOS_API_KEY"
          value_from {
            secret_key_ref {
              name = "nexos-api-key"
              key  = "latest"
            }
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "public_invoker" {
  service  = google_cloud_run_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}


resource "google_secret_manager_secret_iam_member" "cloudrun_access" {
  secret_id = "nexos-api-key"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:213497522537-compute@developer.gserviceaccount.com"
}