provider "google" {
  region = "asia-northeast1"
}

resource "google_cloud_run_service" "default" {
  name     = "scraping"
  location = "asia-northeast1"

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "1"
        "run.googleapis.com/timeoutSeconds" = "300"
      }
    }
    spec {
      containers {
        image = "gcr.io/develop-matsushima/scraping:latest"

        resources {
          limits = {
            memory = "512Mi"
            cpu    = "1"
          }
        }

        ports {
          container_port = 8080
        }

        env {
          name  = "DATABASE_NAME"
          value = "zerosense"
        }

        env {
          name  = "DATABASE_USER"
          value = "kengo"
        }

        env {
          name  = "DATABASE_PASSWORD"
          value = "5W69E2yH7X"
        }

        env {
          name  = "DATABASE_PORT"
          value = "5432"
        }

        env {
          name  = "DJANGO_DEBUG"
          value = "False"
        }

        env {
          name  = "DATABASE_HOST"
          value = "/cloudsql/develop-matsushima:asia-northeast1:develop"
        }

        env {
          name  = "$PORT"
          value = "8080"
        }


      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}
