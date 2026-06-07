terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable GCP Services
resource "google_project_service" "services" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com"
  ])

  service            = each.key
  disable_on_destroy = false
}

# 2. Random ID for Storage Bucket (ensures global uniqueness)
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 3. Cloud Storage Bucket for Source Code Archives
resource "google_storage_bucket" "source_bucket" {
  name                        = "sls-benchmark-src-${lower(var.project_id)}-${random_id.bucket_suffix.hex}"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [google_project_service.services]
}

# 4. Upload Zip Files to Cloud Storage (zipped via zip_sources.py helper)
resource "google_storage_bucket_object" "source_zip" {
  for_each = {
    python = "${path.module}/files/python.zip"
    nodejs = "${path.module}/files/nodejs.zip"
    java   = "${path.module}/files/java.zip"
  }

  name   = "${each.key}-${filemd5(each.value)}.zip"
  bucket = google_storage_bucket.source_bucket.name
  source = each.value
}

# Local variables for generating 15 benchmark function resources
locals {
  runtimes = ["python311", "nodejs20", "java17"]
  memories = [128, 256, 512, 1024, 2048]

  # Generate combination map of: "{prefix}_{memory}"
  functions = {
    for pair in setproduct(local.runtimes, local.memories) :
    "${pair[0] == "python311" ? "py" : pair[0] == "nodejs20" ? "node" : "java"}_${pair[1]}" => {
      runtime     = pair[0]
      memory      = pair[1]
      runtime_key = pair[0] == "python311" ? "python" : pair[0] == "nodejs20" ? "nodejs" : "java"
      entry_point = pair[0] == "python311" ? "google_handler" : pair[0] == "nodejs20" ? "googleHandler" : "com.serverless.benchmark.GoogleFunction"
    }
  }
}

data "google_project" "project" {}

# IAM permissions needed by Cloud Build to build the function images
locals {
  build_service_accounts = [
    "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com",
    "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  ]
  build_roles = [
    "roles/logging.logWriter",
    "roles/storage.objectViewer",
    "roles/artifactregistry.writer"
  ]
  iam_bindings = {
    for pair in setproduct(local.build_service_accounts, local.build_roles) :
    replace(replace("${pair[0]}-${pair[1]}", "serviceAccount:", ""), "roles/", "") => {
      member = pair[0]
      role   = pair[1]
    }
  }
}

resource "google_project_iam_member" "build_permissions" {
  for_each = local.iam_bindings

  project = var.project_id
  role    = each.value.role
  member  = each.value.member
}

# 6. Deploy Google Cloud Functions (Gen 2)
resource "google_cloudfunctions2_function" "benchmark_functions" {
  for_each = local.functions

  name        = each.key
  location    = var.region
  description = "Serverless benchmark function for ${each.value.runtime} and ${each.value.memory}MB"

  build_config {
    runtime     = each.value.runtime
    entry_point = each.value.entry_point
    source {
      storage_source {
        bucket = google_storage_bucket.source_bucket.name
        object = google_storage_bucket_object.source_zip[each.value.runtime_key].name
      }
    }
  }

  service_config {
    max_instance_count = var.max_instance_count
    min_instance_count = 0
    available_memory   = "${each.value.memory}Mi"
    timeout_seconds    = 60
  }

  depends_on = [
    google_project_service.services,
    google_project_iam_member.build_permissions
  ]
}

# 7. Grant Unauthenticated Invocation (Public Access) to the Cloud Run Service
resource "google_cloud_run_service_iam_member" "public_access" {
  for_each = google_cloudfunctions2_function.benchmark_functions

  location = each.value.location
  project  = each.value.project
  service  = each.value.service_config[0].service
  role     = "roles/run.invoker"
  member   = "allUsers"
}
