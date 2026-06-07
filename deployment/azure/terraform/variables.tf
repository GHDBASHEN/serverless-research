variable "location" {
  type        = string
  description = "The Azure region to deploy resources to"
  default     = "Australia Central"
}

variable "app_name" {
  type        = string
  description = "The application name prefix for Azure resources"
  default     = "sls-benchmark-az"
}
