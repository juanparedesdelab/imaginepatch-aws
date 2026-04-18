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

## ADR-007 — IAM Admin user: juan-admin with AdministratorAccess

**Date:** 2026-04-07
**Status:** Accepted

**Context:**
No human admin user existed outside of root. All elevated operations
required using the root account which violates AWS security best practices.
A human admin seat is needed for day-to-day account management, IAM
changes, and anything requiring elevated permissions beyond the scoped
developer policy.

**Options considered:**
- Use root account for admin tasks
- Create a custom scoped admin policy
- Use AWS managed AdministratorAccess policy for a dedicated admin user

**Decision:** Dedicated admin user with AWS managed AdministratorAccess

**Reasoning:**
Using root for operations is a security anti-pattern. A dedicated human
admin user with AdministratorAccess is the correct AWS approach — it
provides full account management capability while keeping root credentials
locked away. Unlike the Terraform service account, this is a human login
with console access. The choice of AWS managed AdministratorAccess over
a custom policy is deliberate — the admin role by definition needs full
access, and a custom policy attempting to replicate that adds complexity
without security benefit.

**Users created:**
- `juan-admin` — human admin, AdministratorAccess, console enabled
- Group: `imaginepatch-admins`

**Root account usage:** Reserved for account-level only tasks such as
changing payment methods or closing the account. Never used for
day-to-day operations.

---

## ADR-008 — DNS: Cloudflare over Route 53 for DNS resolution

**Date:** 2026-04-07
**Status:** Accepted

**Context:**
After creating the Lightsail instance and configuring Route 53 hosted zone
with correct A records pointing to the static IP (34.196.169.203), the
domain imaginepatch.com was completely unresolvable. All DNS resolvers
including Google (8.8.8.8), Cloudflare (1.1.1.1), and OpenDNS returned
"Server failed". Direct queries to AWS nameservers returned "Query refused".

**Root cause identified:**
DNSViz analysis showed 16 DNSSEC errors and a broken chain of trust between
the .com TLD and the imaginepatch.com hosted zone. The domain was previously
registered with GoDaddy which had DNSSEC enabled. When the domain was
transferred to Route 53, orphaned DNSSEC records remained at the .com TLD
registry level, causing all DNSSEC-validating resolvers to reject the domain.
Route 53 showed DnssecKeys as empty, making the issue invisible from the
console. AWS basic support plan did not include technical cases.

**Options considered:**
- Upgrade AWS support plan to get technical assistance
- Enable DNSSEC signing in Route 53 to fix the broken chain
- Switch DNS to Cloudflare

**Decision:** Cloudflare for DNS and SSL

**Reasoning:**
Cloudflare bypasses the broken DNSSEC chain entirely by using its own
nameservers. Switching nameservers in Route 53 Registered Domains from
AWS to Cloudflare resolved the issue within minutes. Cloudflare also
provides free SSL, global CDN, and DDoS protection — replacing the need
for CloudFront in Phase 1 at zero cost. The original architecture planned
CloudFront for CDN and SSL termination, but Cloudflare provides equivalent
functionality for free with simpler setup.

**Changes from original architecture:**
- Route 53 retained for domain registration only
- Cloudflare handles DNS resolution, CDN, and SSL/TLS
- CloudFront removed from Phase 1 architecture
- Architecture diagram updated to reflect this change

**Lessons learned:**
- Always check DNSSEC status when transferring domains between registrars
- DNSViz is an essential tool for diagnosing DNS chain issues
- Having a scoped IAM policy for the Terraform user caused initial CLI
  access issues — the admin profile was needed for route53domains commands
- Cloudflare free tier is a viable and superior alternative to CloudFront
  for small to medium traffic sites

---

## ADR-009 — Frontend: Blocksy + Elementor over custom child theme (Phase 1)

**Date:** 2026-04-17
**Status:** Accepted

**Context:**
A full design system and three HTML prototype pages (homepage, shop, product)
were built prior to WordPress setup. The prototypes define the exact visual
direction: dark background (#000000/#1A0A2E), purple (#7B2FBE) and gold
(#F5C842) palette, Y2K Magical / Mystical aesthetic, Pacifico/Fredoka One/
Nunito/Cormorant Garamond font stack. The question was how to bring this
approved design into WordPress and WooCommerce.

**Options considered:**
- Convert HTML prototypes into a custom WooCommerce child theme (PHP templates)
- Use Blocksy (free base theme) + Elementor (page builder) to recreate the design
- Find a third-party dark WooCommerce theme and customize it to match

**Decision:** Blocksy + Elementor for Phase 1

**Reasoning:**
The HTML prototypes serve as a pixel-perfect reference. Blocksy is a
lightweight, fast base theme with strong WooCommerce hooks and full Elementor
compatibility. It acts as a blank canvas without imposing its own design
opinions, allowing the approved design system to be applied globally via
Blocksy's customizer (colors, fonts) and page-by-page via Elementor.
Blocksy's free tier is sufficient to evaluate fit before any cost is incurred.

A custom child theme (Option A) is the technically superior long-term
solution and is planned for Phase 2 — it will also serve as a stronger
portfolio piece demonstrating PHP/WordPress template development. However,
it requires significant development time that delays revenue generation,
which is the Phase 1 priority.

Third-party dark themes (Option C) were ruled out because they have strong
built-in design opinions that would conflict with the approved design system
and require more effort to override than building cleanly with Blocksy.

**Phase 2 note:**
The custom child theme conversion is a planned portfolio milestone. The
Blocksy + Elementor implementation serves as the functional specification
for that conversion.

**Store manager impact:**
Elementor's visual editor allows Angie to manage page content independently
without code changes, which is a requirement given the division of
responsibilities on this project.

*New decisions will be added to this file as the project evolves.*
*Format: ADR-XXX — short title, date, status, context, options, decision, reasoning.*