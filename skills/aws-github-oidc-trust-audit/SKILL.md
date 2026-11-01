---
name: aws-github-oidc-trust-audit
description: Use when reviewing AWS IAM role trust policies for GitHub Actions OIDC federation before deploying infrastructure. Run a read-only offline scan of assume-role policy JSON for overly broad GitHub subject claims, missing audience restrictions and unsupported condition operators; does not validate live AWS IAM, repository environment protection or the caller's actual permissions.
license: MIT
compatibility: Python 3.10+ standard library, local JSON files only; no network or AWS credentials.
---

# GitHub OIDC Trust Audit

## Trigger
Use this Skill when an agent reviews AWS role trust policies using GitHub Actions OIDC, checks a Terraform-generated JSON assume-role document, or needs reproducible evidence in a PR.

## Do not trigger
Do not use to certify production IAM security, validate a non-GitHub OIDC provider, or conclude effective permissions. An IAM policy may include separate explicit denies, permission boundaries, or conditional logic outside this narrow model.

## Procedure
1. Identify a local **trust policy** JSON file (not an IAM permissions policy); avoid collecting secret credentials.
2. Read [references/MODEL.md](references/MODEL.md) before drawing conclusions.
3. Run `python scripts/audit.py examples/review.json --format json --fail-on high` for a synthetic sample, then run the CLI against the user's selected local JSON.
4. Summarize exact `code`, severity, filename and statement index. Never present a REVIEW finding as confirmed exploitation.
5. Check GitHub's OIDC `sub` and `aud` conventions, and consider GitHub environments plus AWS role policy context in a manual review.
6. Recommend narrow repository/branch restrictions where appropriate; ask before editing live IAM.
7. If exit status is 2, stop: malformed input is not a clean audit.

## Exit codes
- 0: configured threshold not reached
- 1: at least one finding at threshold
- 2: invalid/unreadable input

## Boundaries
Read-only, no shell execution of input data, no cloud network calls or IAM changes. Does not model full IAM policy evaluation, custom OIDC subject templates, or GitHub environment protection enforcement.