terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "admin"
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

# NOTE: aws_lightsail_static_ip and aws_lightsail_instance_public_ports
# do not support Terraform import. These resources are managed manually
# in the AWS console until Phase 2 migration to EC2.