variable "region" {
  type        = string
  description = "The AWS region to deploy resources to"
  default     = "us-east-1"
}

variable "app_name" {
  type        = string
  description = "The application name prefix for AWS resources"
  default     = "sls-benchmark-aws"
}
