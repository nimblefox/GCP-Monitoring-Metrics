resource "google_cloud_run_service" "metrics_exporter" {
  name     = "metrics-exporter"
  location = var.region
  project  = var.gcp_project_id
  template {
    spec {
      containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_scheduler_job" "scheduler" {
  name      = "daily-metric-exporter-job"
  schedule  = "0 12 * * *"
  time_zone = "US/Central"
  http_target {
    http_method = "POST"
    uri         = google_cloud_run_service.metrics_exporter.status[0].url
    oidc_token {
      service_account_email = var.service_account_email
    }
  }
}

resource "google_bigquery_dataset" "metrics_dataset" {
  dataset_id  = "metrics-dataset"
  description = "This dataset has tables of monitoring metrics"
  project     = var.gcp_project_id
}

resource "google_bigquery_table" "metrics_table" {
  dataset_id          = google_bigquery_dataset.metrics_dataset.dataset_id
  table_id            = "metrics-table"
  deletion_protection = false
  time_partitioning {
    type = "DAY"
  }

  schema = <<EOF
[
  {
    "name": "Time",
    "type": "TIMESTAMP",
    "mode": "NULLABLE",
    "description": "Time of metric data"
  },
  {
    "name": "Value",
    "type": "BIGNUMERIC",
    "mode": "NULLABLE",
    "description": "Value of Metric"
  }
]
EOF

}