# ===========================================================================
#  Cloud Resume Challenge — infrastructure/environments/dev/main.tf
#  Step 12 — IaC root: wires both modules + Terraform remote state in S3
# ===========================================================================

terraform {
  required_version = ">= 1.7"

  # ── Remote state backend (Step 13) ───────────────────────────────────────
  # Create this bucket + table ONCE manually (or via a bootstrap script)
  # before running terraform init.
  backend "s3" {
    bucket         = "cloud-resume-tfstate-ACCOUNT_ID"   # ← replace
    key            = "cloud-resume/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "cloud-resume-tfstate-lock"          # for state locking
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------
variable "aws_region"    { default = "ap-south-1" }
variable "domain_name"   { description = "Your resume domain e.g. resume.example.com" }
variable "root_domain"   { description = "Root hosted zone domain e.g. example.com" }

# ---------------------------------------------------------------------------
# Module: Static Site  (S3 + CloudFront + Route 53 + ACM)
# ---------------------------------------------------------------------------
module "static_site" {
  source      = "../../modules/static-site"
  domain_name = var.domain_name
  root_domain = var.root_domain
}

# ---------------------------------------------------------------------------
# Module: API Backend  (DynamoDB + Lambda + API Gateway)
# ---------------------------------------------------------------------------
module "api_backend" {
  source         = "../../modules/api-backend"
  allowed_origin = "https://${var.domain_name}"
}

# ---------------------------------------------------------------------------
# Outputs — printed after terraform apply
# ---------------------------------------------------------------------------
output "resume_url"      { value = module.static_site.resume_url }
output "api_endpoint"    { value = module.api_backend.api_endpoint }
output "s3_bucket"       { value = module.static_site.s3_bucket_name }
output "cloudfront_id"   { value = module.static_site.cloudfront_dist_id }
