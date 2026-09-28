terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket       = "imaginepatch-terraform-state-767398024800"
    key          = "root/terraform.tfstate"
    region       = "us-east-1"
    profile      = "default"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "default"
}

# ── LIGHTSAIL INSTANCE ─────────────────────────────────────────────────────────
resource "aws_lightsail_instance" "imaginepatch_production" {
  name              = "imaginepatch-production"
  availability_zone = "us-east-1a"
  blueprint_id      = "wordpress_ls_1_0"
  bundle_id         = "small_3_0"
  key_pair_name     = "LightsailDefaultKeyPair"

  add_on {
    type          = "AutoSnapshot"
    snapshot_time = "00:00"
    status        = "Enabled"
  }

  tags = {
    project     = "imaginepatch"
    environment = "production"
  }
}

# ── CLOUDTRAIL AUDIT LOGGING ──────────────────────────────────────────────────
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "imaginepatch-cloudtrail-logs-767398024800"

  tags = {
    project     = "imaginepatch"
    environment = "production"
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    id     = "expire-logs-90-days"
    status = "Enabled"

    filter {}

    expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AWSCloudTrailAclCheck"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = "arn:aws:s3:::imaginepatch-cloudtrail-logs-767398024800"
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:cloudtrail:us-east-1:767398024800:trail/imaginepatch-trail"
          }
        }
      },
      {
        Sid       = "AWSCloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "arn:aws:s3:::imaginepatch-cloudtrail-logs-767398024800/AWSLogs/767398024800/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl"  = "bucket-owner-full-control"
            "aws:SourceArn" = "arn:aws:cloudtrail:us-east-1:767398024800:trail/imaginepatch-trail"
          }
        }
      }
    ]
  })
}

resource "aws_cloudtrail" "imaginepatch" {
  name                          = "imaginepatch-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  is_multi_region_trail         = true
  include_global_service_events = true
  enable_log_file_validation    = true

  tags = {
    project     = "imaginepatch"
    environment = "production"
  }

  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]
}

# ── TERRAFORM REMOTE STATE BUCKET ─────────────────────────────────────────────
resource "aws_s3_bucket" "terraform_state" {
  bucket = "imaginepatch-terraform-state-767398024800"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    project     = "imaginepatch"
    environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    id     = "expire-old-state-versions-90-days"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

# NOTE: aws_lightsail_static_ip and aws_lightsail_instance_public_ports
# do not support Terraform import. These resources are managed manually
# in the AWS console until Phase 2 migration to EC2.