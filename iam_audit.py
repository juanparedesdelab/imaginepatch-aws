#!/usr/bin/env python3
"""
IAM Audit Script — Imagine Patch AWS Account
==============================================
Audits IAM users, groups, policies, access keys, and MFA status
against the structure documented in DECISIONS.md (ADR-005, ADR-007).

Usage:
    pip install boto3 --break-system-packages
    python3 iam_audit.py [--profile PROFILE_NAME]

Requires read-only IAM permissions:
    iam:ListUsers, iam:ListGroups, iam:ListGroupsForUser,
    iam:ListAttachedUserPolicies, iam:ListAttachedGroupPolicies,
    iam:ListUserPolicies, iam:ListAccessKeys,
    iam:GetAccessKeyLastUsed, iam:ListMFADevices,
    iam:GetLoginProfile, iam:GetAccountPasswordPolicy
"""

import argparse
import sys
from datetime import datetime, timezone

try:
    import boto3
    from botocore.exceptions import ClientError, ProfileNotFound
except ImportError:
    sys.exit("boto3 not installed. Run: pip install boto3 --break-system-packages")


# Expected structure from DECISIONS.md (ADR-005, ADR-007)
EXPECTED_GROUPS = {
    "imaginepatch-admins": "AdministratorAccess (ADR-007) — max 1 human user",
    "imaginepatch-developers": "Full infra access — max 1 user (Juan)",
    "imaginepatch-store-managers": "WooCommerce + S3 read — max 2 users",
    "imaginepatch-designers": "S3 media upload only — max 2 users",
    "imaginepatch-finance-owners": "Billing + Cost Explorer — max 2 users",
    "imaginepatch-read-only": "Get/List/Describe — max 2 users",
}


def days_since(dt):
    if dt is None:
        return None
    now = datetime.now(timezone.utc)
    return (now - dt).days


def audit(profile_name=None):
    try:
        session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        iam = session.client("iam")
    except ProfileNotFound:
        sys.exit(f"AWS profile '{profile_name}' not found. Check ~/.aws/credentials")

    print("=" * 70)
    print("IMAGINE PATCH — IAM AUDIT")
    print(f"Run at: {datetime.now(timezone.utc).isoformat()}")
    print(f"Profile: {profile_name or 'default'}")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Account password policy
    # ------------------------------------------------------------
    print("\n--- ACCOUNT PASSWORD POLICY ---")
    try:
        policy = iam.get_account_password_policy()["PasswordPolicy"]
        for k, v in policy.items():
            print(f"  {k}: {v}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            print("  ⚠️  No custom password policy set (using AWS defaults)")
        else:
            print(f"  Error: {e}")

    # ------------------------------------------------------------
    # 2. Groups vs expected structure
    # ------------------------------------------------------------
    print("\n--- GROUPS ---")
    groups_resp = iam.list_groups()
    existing_groups = {g["GroupName"] for g in groups_resp["Groups"]}

    for expected, desc in EXPECTED_GROUPS.items():
        status = "✅" if expected in existing_groups else "❌ MISSING"
        print(f"  {status}  {expected}  —  {desc}")

    extra_groups = existing_groups - set(EXPECTED_GROUPS.keys())
    if extra_groups:
        print("\n  ⚠️  Unexpected groups not in ADR-005:")
        for g in extra_groups:
            print(f"     - {g}")

    # Attached policies per group
    print("\n--- GROUP POLICIES ---")
    for g in groups_resp["Groups"]:
        gname = g["GroupName"]
        attached = iam.list_attached_group_policies(GroupName=gname)["AttachedPolicies"]
        inline = iam.list_group_policies(GroupName=gname)["PolicyNames"]
        print(f"\n  Group: {gname}")
        if attached:
            for p in attached:
                print(f"    Managed policy: {p['PolicyName']}")
        if inline:
            for p in inline:
                print(f"    Inline policy:  {p}")
        if not attached and not inline:
            print("    (no policies attached)")

    # ------------------------------------------------------------
    # 3. Users — groups, policies, keys, MFA, console access
    # ------------------------------------------------------------
    print("\n" + "=" * 70)
    print("USERS")
    print("=" * 70)

    users = iam.list_users()["Users"]

    for user in users:
        uname = user["UserName"]
        print(f"\nUser: {uname}")
        print(f"  Created: {user['CreateDate'].date()}")

        # Group memberships
        groups = iam.list_groups_for_user(UserName=uname)["Groups"]
        if groups:
            for g in groups:
                print(f"  Group: {g['GroupName']}")
        else:
            print("  Group: (none)")

        # Directly attached policies (flag — should generally be via groups only)
        attached = iam.list_attached_user_policies(UserName=uname)["AttachedPolicies"]
        inline = iam.list_user_policies(UserName=uname)["PolicyNames"]
        if attached:
            for p in attached:
                flag = " ⚠️  directly attached (consider moving to a group)"
                print(f"  Managed policy: {p['PolicyName']}{flag}")
        if inline:
            for p in inline:
                print(f"  Inline policy:  {p}  ⚠️  directly attached")

        # Console access (login profile)
        try:
            iam.get_login_profile(UserName=uname)
            console_access = True
        except ClientError as e:
            console_access = False if e.response["Error"]["Code"] == "NoSuchEntity" else None
        print(f"  Console access: {'Yes' if console_access else 'No'}")

        # MFA devices
        mfa = iam.list_mfa_devices(UserName=uname)["MFADevices"]
        if console_access:
            mfa_status = f"✅ {len(mfa)} device(s)" if mfa else "❌ NO MFA — risk for console user"
        else:
            mfa_status = f"{len(mfa)} device(s)" if mfa else "(n/a — no console access)"
        print(f"  MFA: {mfa_status}")

        # Access keys — age and last used
        keys = iam.list_access_keys(UserName=uname)["AccessKeyMetadata"]
        if keys:
            for k in keys:
                age = days_since(k["CreateDate"])
                try:
                    last_used_resp = iam.get_access_key_last_used(AccessKeyId=k["AccessKeyId"])
                    last_used = last_used_resp["AccessKeyLastUsed"].get("LastUsedDate")
                    last_used_str = last_used.date().isoformat() if last_used else "never used"
                except ClientError:
                    last_used_str = "unknown"

                flag = ""
                if age and age > 90:
                    flag = "  ⚠️  >90 days old — consider rotating"
                print(f"  Access key: {k['AccessKeyId']} | Status: {k['Status']} | "
                      f"Age: {age}d | Last used: {last_used_str}{flag}")
        else:
            print("  Access keys: (none)")

    # ------------------------------------------------------------
    # 4. Summary against ADR-005 user count limits
    # ------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY CHECKS")
    print("=" * 70)
    print(f"Total IAM users: {len(users)}")
    print(f"Total groups: {len(existing_groups)}")
    print("\nReview the output above for:")
    print("  - Any user with console access but NO MFA (🔴 highest priority)")
    print("  - Any directly-attached policies bypassing group structure")
    print("  - Access keys older than 90 days")
    print("  - Missing groups vs ADR-005 structure")
    print("  - Root account should NOT appear here (it's separate from IAM)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IAM audit for Imagine Patch")
    parser.add_argument("--profile", help="AWS CLI profile name (e.g. juan-admin)", default=None)
    args = parser.parse_args()
    audit(args.profile)
