provider "google" {
  # apikeyはterraformの terraform variables にて指定する。(jsonを一行にして入力する必要あり)
  # credentials = file("key.json")
  # credentials = var.api_key
  region  = "asia-northeast1"
  project = "develop-matsushima"
}

resource "google_cloud_run_service" "default" {
  name     = "zerosense-scraping"
  location = "asia-northeast1"

  template {
    metadata {
      annotations = {
        # インスタンスの最小数
        "autoscaling.knative.dev/minScale" = "0"
        # インスタンスの最大数
        "autoscaling.knative.dev/maxScale" = "1"
        #  リクエストタイムアウト
        "run.googleapis.com/timeoutSeconds" = "300"


      }
    }
    spec { # インスタンスが同時に処理するリクエスト数
      container_concurrency = 1
      containers {
        # ビルドするイメージを指定
        image = "asia.gcr.io/develop-matsushima/scraping:latest"

        resources {
          limits = {
            memory = "1Gi"
            cpu    = "2"
          }
        }

        ports {
          container_port = 8080
        }

        env {
          name  = "DATABASE_NAME"
          value = var.db_name
        }

        env {
          name  = "DATABASE_USER"
          value = var.db_user
        }

        env {
          name  = "DATABASE_PASSWORD"
          value = var.db_password
        }

        env {
          name  = "DATABASE_PORT"
          value = "5432"
        }

        env {
          name  = "DJANGO_DEBUG"
          value = var.django_debug
        }

        env {
          name  = "DATABASE_HOST"
          value = var.db_host
        }

        env {
          name  = "$PORT"
          value = "8080"
        }

        env {
          name  = "$LOCAL"
          value = "false"
        }


      }
    }
  }

  traffic {
    # parcent%のトラフィックを指定のリビジョンに送る
    percent         = 100
    latest_revision = true
  }
  # リビジョン名を自動的に生成
  autogenerate_revision_name = true
}
