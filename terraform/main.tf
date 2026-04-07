terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_policy" "developer" {
  name        = "imaginepatch-developer-policy"
  description = "Full infrastructure access for Imagine Patch developer"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "LightsailFullAccess"
        Effect   = "Allow"
        Action   = ["lightsail:*"]
        Resource = "*"
      },
      {
        Sid      = "S3FullAccess"
        Effect   = "Allow"
        Action   = ["s3:*"]
        Resource = "*"
      },
      {
        Sid      = "Route53FullAccess"
        Effect   = "Allow"
        Action   = ["route53:*"]
        Resource = "*"
      },
      {
        Sid      = "CloudFrontFullAccess"
        Effect   = "Allow"
        Action   = ["cloudfront:*"]
        Resource = "*"
      },
      {
        Sid      = "IAMReadOnly"
        Effect   = "Allow"
        Action   = ["iam:Get*", "iam:List*"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "store_manager" {
  name        = "imaginepatch-store-manager-policy"
  description = "S3 read, SES email, and CloudWatch monitoring for store managers"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3ReadAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = "*"
      },
      {
        Sid    = "SESAccess"
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail",
          "ses:GetSendStatistics",
          "ses:ListIdentities"
        ]
        Resource = "*"
      },
      {
        Sid    = "CloudWatchReadOnly"
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "designer" {
  name        = "imaginepatch-designer-policy"
  description = "S3 upload and manage access to media bucket only"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3MediaUpload"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          "arn:aws:s3:::imaginepatch-media",
          "arn:aws:s3:::imaginepatch-media/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "finance" {
  name        = "imaginepatch-finance-policy"
  description = "Billing, Cost Explorer, and budget read access for finance owners"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BillingAccess"
        Effect = "Allow"
        Action = [
          "aws-portal:ViewBilling",
          "aws-portal:ViewUsage",
          "aws-portal:ViewAccount",
          "budgets:ViewBudget",
          "budgets:DescribeBudgetAction",
          "budgets:DescribeBudgetActionsForAccount",
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
          "ce:GetDimensionValues",
          "ce:GetReservationUtilization",
          "ce:GetSavingsPlansUtilization",
          "ce:ListCostCategoryDefinitions"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "readonly" {
  name        = "imaginepatch-readonly-policy"
  description = "Read-only access across all Imagine Patch services for auditing and monitoring"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "LightsailReadOnly"
        Effect = "Allow"
        Action = [
          "lightsail:GetInstance",
          "lightsail:GetInstances",
          "lightsail:GetInstanceState",
          "lightsail:GetInstanceMetricData",
          "lightsail:GetStaticIp",
          "lightsail:GetStaticIps",
          "lightsail:GetDomain",
          "lightsail:GetDomains",
          "lightsail:GetDisk",
          "lightsail:GetDisks",
          "lightsail:GetInstanceSnapshot",
          "lightsail:GetInstanceSnapshots",
          "lightsail:GetDiskSnapshot",
          "lightsail:GetDiskSnapshots",
          "lightsail:GetBundles",
          "lightsail:GetBlueprints",
          "lightsail:GetRegions"
        ]
        Resource = "*"
      },
      {
        Sid    = "ReadOnlyAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketPolicy",
          "route53:Get*",
          "route53:List*",
          "cloudfront:Get*",
          "cloudfront:List*",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms",
          "iam:Get*",
          "iam:List*",
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
          "budgets:ViewBudget"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_group" "developers" {
  name = "imaginepatch-developers"
}

resource "aws_iam_group" "store_managers" {
  name = "imaginepatch-store-managers"
}

resource "aws_iam_group" "designers" {
  name = "imaginepatch-designers"
}

resource "aws_iam_group" "finance_owners" {
  name = "imaginepatch-finance-owners"
}

resource "aws_iam_group" "readonly" {
  name = "imaginepatch-readonly"
}

resource "aws_iam_group_policy_attachment" "developers" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.developer.arn
}

resource "aws_iam_group_policy_attachment" "store_managers" {
  group      = aws_iam_group.store_managers.name
  policy_arn = aws_iam_policy.store_manager.arn
}

resource "aws_iam_group_policy_attachment" "designers" {
  group      = aws_iam_group.designers.name
  policy_arn = aws_iam_policy.designer.arn
}

resource "aws_iam_group_policy_attachment" "finance_owners" {
  group      = aws_iam_group.finance_owners.name
  policy_arn = aws_iam_policy.finance.arn
}

resource "aws_iam_group_policy_attachment" "readonly" {
  group      = aws_iam_group.readonly.name
  policy_arn = aws_iam_policy.readonly.arn
}