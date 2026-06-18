terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  s3_use_path_style = true

  endpoints {
    s3 = var.localstack_endpoint
  }
}

resource "aws_s3_bucket" "drive" {
  bucket = var.bucket_name
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "localstack_endpoint" {
  type    = string
  default = "http://localhost:4566"
}

variable "bucket_name" {
  type    = string
  default = "drive-clone-bucket"
}

output "bucket_name" {
  description = "Nombre del bucket creado"
  value       = aws_s3_bucket.drive.bucket
}
