---
name: gha-reusable-permission-audit
description: Audit local GitHub Actions caller workflows for reusable workflow trust boundaries, mutable external refs, inherited secrets and GITHUB_TOKEN write permissions. Use for workflows with job-level uses; do not use to certify GitHub repository settings or inspect callee behavior.
license: MIT
compatibility: Python 3.10+; PyYAML 6.x; offline one local workflow YAML file.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# GitHub Actions Reusable Permission Audit

## Activate / avoid
Use when a user supplies `.github/workflows/*.yml` calling reusable workflows with `jobs.<job>.uses`, `secrets: inherit`, commit pins, or GITHUB_TOKEN permissions. Do not use to approve callee source code, detect secret values, infer organization policy, or claim a workflow is secure.

## Procedure
1. Confirm the authorized specific caller YAML; never enumerate credentials.
2. Read [rules](references/RULES.md).
3. Install `python -m pip install -r requirements.txt`.
4. Run `python scripts/audit.py examples/safe.yml` and `python scripts/audit.py examples/review.yml --json`.
5. Run `python scripts/audit.py path/to/caller.yml --json`; 0=no modeled findings, 1=review, 2=invalid file.
6. Explain rule IDs and permissions inheritance; recommend full SHA pin, explicit least-privilege token and named minimal secrets, then review the callee separately.

No network, Actions execution, repository settings lookup or external caller resolution. Never echo secret contents or names.
