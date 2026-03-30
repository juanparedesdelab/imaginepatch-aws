# Architecture Decision Records — Imagine Patch AWS Infrastructure

This document records every major infrastructure and security decision made
during the build of Imagine Patch on AWS. Each decision includes context,
options considered, the choice made, and the reasoning behind it.

---

## ADR-001 — Cloud platform: AWS

**Date:** 2026-03-29
**Status:** Accepted

**Context:**
Needed a cloud platform to host the Imagine Patch WooCommerce store.
Also serves as a portfolio project to demonstrate cloud computing skills.

**Options considered:**
- AWS
- Google Cloud Platform
- DigitalOcean

**Decision:** AWS

**Reasoning:**
AWS is the industry standard for cloud computing roles. Using AWS maximizes
portfolio value and directly supports the long-term goal of moving into
cloud computing professionally. AWS also offers the widest range of services
for future scaling.

---

## ADR-002 — Compute: Lightsail over EC2 (Phase 1)

**Date:** 2026-03-29
**Status:** Accepted

**Context:**
Needed to choose a compute service to host WordPress and WooCommerce.
The store is starting from zero with no existing traffic or revenue.

**Options considered:**
- EC2 with full VPC architecture
- Lightsail WordPress blueprint

**Decision:** Lightsail for Phase 1, migrate to EC2 for Phase 2

**Reasoning:**
Lightsail provides predictable flat-rate pricing ($10/month all-inclusive)
vs EC2 which would run $25-35/month with all required add-ons. For a new
store with no proven traffic, Lightsail reduces financial risk while still
running on AWS infrastructure. The planned migration to EC2 in Phase 2
demonstrates deliberate scaling decisions — a stronger portfolio story than
starting with over-engineered infrastructure.

---

## ADR-003 — Infrastructure as Code: Terraform over CloudFormation

**Date:** 2026-03-29
**Status:** Accepted

**Context:**
Needed an IaC tool to document and version all AWS infrastructure changes.

**Options considered:**
- Terraform (HashiCorp)
- AWS CloudFormation

**Decision:** Terraform

**Reasoning:**
Terraform is cloud-agnostic and works across AWS, GCP, and Azure. This
maximizes career value since Terraform skills transfer across employers and
cloud providers. CloudFormation is AWS-only, which limits portfolio
applicability. All infrastructure changes are committed to GitHub to
demonstrate version-controlled, reproducible infrastructure.

---

## ADR-004 — POD Supplier: Printful over Printify (Phase 1)

**Date:** 2026-03-29
**Status:** Accepted

**Context:**
Needed a print-on-demand supplier integrated with WooCommerce.

**Options considered:**
- Printful (in-house fulfillment)
- Printify (third-party provider network)

**Decision:** Printful for Phase 1

**Reasoning:**
Starting from zero with no existing customer base means first impressions
are critical. Printful's in-house fulfillment provides consistent quality
and reliable delivery times, reducing the risk of bad reviews early on.
Printify offers lower base costs but quality varies by provider. Once the
store is proven and volume increases, Printify will be re-evaluated for
margin optimization in Phase 2.

---

## ADR-005 — IAM Structure: Groups and least-privilege policies

**Date:** 2026-03-29
**Status:** Accepted

**Context:**
Needed to define who has access to what in the AWS account. Currently
two active users (Juan and Angie) with potential for future team members.

**Options considered:**
- Single admin user for everything
- Role-based groups with scoped policies

**Decision:** Role-based groups with scoped policies

**Reasoning:**
Following the principle of least privilege from day one. Each group has
only the permissions required for its function — nothing more. This
reduces the blast radius of any accidental or malicious action. It also
scales cleanly if new team members join. Using AdministratorAccess for
the Terraform IAM user was a temporary measure — replaced by a scoped
policy as the first security hardening step.

**Groups created:**
- `imaginepatch-developers` — 1 user max (Juan). Full infrastructure access.
- `imaginepatch-store-managers` — 2 users max. WooCommerce and S3 read only.
- `imaginepatch-designers` — 2 users max. S3 media upload only.
- `imaginepatch-finance-owners` — 2 users max. Billing and Cost Explorer only.
- `imaginepatch-read-only` — 2 users max. Get/List/Describe across all services.

---

## ADR-006 — Root account: locked down, never used for operations

**Date:** 2026-03-29
**Status:** Accepted

**Context:**
AWS root account has unrestricted access to everything including billing
and account closure. Using it for day-to-day operations is a security risk.

**Decision:** Root account reserved for account-level tasks only

**Reasoning:**
Root credentials are never used for infrastructure work, Terraform, or
any operational task. All work is done through IAM users with scoped
permissions. This follows AWS security best practices and demonstrates
security-first thinking for portfolio and career purposes.

---

*New decisions will be added to this file as the project evolves.*
*Format: ADR-XXX — short title, date, status, context, options, decision, reasoning.*