variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID"
  default     = "serverless-research01"
}

variable "region" {
  type        = string
  description = "The GCP region to deploy resources to"
  default     = "us-central1"
}

variable "max_instance_count" {
  type        = number
  description = "The maximum number of concurrent instances for each Cloud Function to prevent quota violations"
  default     = 3
}
