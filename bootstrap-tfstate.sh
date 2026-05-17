#!/usr/bin/env bash
# ===========================================================================
#  Cloud Resume Challenge — scripts/bootstrap-tfstate.sh
#  Run ONCE manually to create the S3 bucket + DynamoDB table
#  that Terraform uses for remote state (Step 13 — remote state backend)
# ===========================================================================
set -euo pipefail

REGION="ap-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET="cloud-resume-tfstate-${ACCOUNT_ID}"
LOCK_TABLE="cloud-resume-tfstate-lock"

echo "==> Creating Terraform remote state bucket: $BUCKET"
aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --create-bucket-configuration LocationConstraint="$REGION"

aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket "$BUCKET" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}
    }]
  }'

aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "==> Creating DynamoDB lock table: $LOCK_TABLE"
aws dynamodb create-table \
  --table-name "$LOCK_TABLE" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "$REGION"

echo ""
echo "✅  Bootstrap complete."
echo "    Bucket:     $BUCKET"
echo "    Lock table: $LOCK_TABLE"
echo ""
echo "Update infrastructure/environments/dev/main.tf backend block:"
echo "  bucket = \"$BUCKET\""
