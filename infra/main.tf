# ─────────────────────────────────────────────────────────────────────────────
# eatguai — Terraform
#
# `terraform apply` does everything:
#   1. Enables required GCP APIs
#   2. Creates Artifact Registry repository
#   3. Builds and pushes Docker image via Cloud Build
#   4. Creates a least-privilege Service Account
#   5. Deploys to Cloud Run
#
# Usage:
#   cd infra/
#   terraform init
#   terraform apply -var-file="terraform.tfvars"
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# ── Variables ─────────────────────────────────────────────────────────────────

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service and Artifact Registry repo name"
  type        = string
  default     = "eatguai"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

# ── Locals ────────────────────────────────────────────────────────────────────

locals {
  image_url = "${var.region}-docker.pkg.dev/${var.project_id}/${var.service_name}/${var.service_name}:${var.image_tag}"
  app_root  = "${path.module}/.."
}

# ── Provider ──────────────────────────────────────────────────────────────────

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── APIs ──────────────────────────────────────────────────────────────────────

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "logging.googleapis.com",
    "aiplatform.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

# ── Artifact Registry ─────────────────────────────────────────────────────────

resource "google_artifact_registry_repository" "eatguai" {
  repository_id = var.service_name
  format        = "DOCKER"
  location      = var.region
  description   = "Docker images for EatguAI"

  depends_on = [google_project_service.apis]
}

# ── Build + Push image via Cloud Build ───────────────────────────────────────
# Runs `gcloud builds submit` as part of terraform apply.
# Triggered only when source files change (tracked via md5 hash).

resource "null_resource" "docker_build" {
  triggers = {
    dockerfile  = filemd5("${local.app_root}/Dockerfile")
    app         = filemd5("${local.app_root}/app_gradiov4.py")
    config      = filemd5("${local.app_root}/config.py")
    models      = filemd5("${local.app_root}/models.py")
    vision      = filemd5("${local.app_root}/core/vision.py")
    recommender = filemd5("${local.app_root}/core/recommender.py")
  }

  provisioner "local-exec" {
    command = <<-EOT
      gcloud builds submit ${local.app_root} \
        --tag=${local.image_url} \
        --project=${var.project_id} \
        --quiet
    EOT
  }

  depends_on = [google_artifact_registry_repository.eatguai]
}

# ── Service Account ───────────────────────────────────────────────────────────

resource "google_service_account" "eatguai" {
  account_id   = "${var.service_name}-sa"
  display_name = "EatguAI Cloud Run Service Account"
}

resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.eatguai.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.eatguai.email}"
}

# ── Cloud Run ─────────────────────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "eatguai" {
  name     = var.service_name
  location = var.region

  template {
    service_account = google_service_account.eatguai.email

    containers {
      image = local.image_url

      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
        cpu_idle = true
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_REGION"
        value = var.region
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  depends_on = [
    google_project_service.apis,
    null_resource.docker_build,
  ]
}

# ── Public access ─────────────────────────────────────────────────────────────

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.eatguai.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Outputs ───────────────────────────────────────────────────────────────────

output "service_url" {
  description = "Public URL of the deployed EatguAI app"
  value       = google_cloud_run_v2_service.eatguai.uri
}

output "image_url" {
  description = "Docker image URL in Artifact Registry"
  value       = local.image_url
}
