resource "google_storage_bucket" "gcs_bucket" {
  name     = "test-bucket-001"
  location = "US"
}