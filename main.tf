provider "google" {
  # apikeyはterraformの terraform variables にて指定する。(jsonを一行にして入力する必要あり)
  # credentials = file("key.json")
  # credentials = var.api_key
  region  = "asia-northeast1"
  project = "develop-matsushima"

}

# resource "google_vpc_access_connector" "vpc_connector" { # VPCコネクタを定義
#   name          = "zerosense-vpc-connector"
#   region        = "asia-northeast1" # リージョンはcloudrun と同じにする
#   network       = "default"
#   ip_cidr_range = "10.221.0.0/28" # VPCネットワークのサブネットと重複しない範囲を選択

# }


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
        # Cloud SQLインスタンスへの接続設定
        "run.googleapis.com/cloudsql-instances" = "develop-matsushima:asia-northeast1:develop"
      }
    }

    spec {

      container_concurrency = 1 # インスタンスが同時に処理するリクエスト数 
      containers {
        # ビルドするイメージを指定
        image = "asia.gcr.io/develop-matsushima/scraping:latest"
        # VPCコネクタの設定を追加


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
          value = "False"
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
