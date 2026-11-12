---
name: gha-environment-gate-audit
description: Audit GitHub Actions workflow deployment jobs against an explicitly supplied GitHub environment-settings inventory. Use for PR reviews of deployment gates, required reviewers, branch restrictions and environment bindings before releases.
license: MIT
compatibility: Python 3.10+ and PyYAML 6; offline, read-only; Claude Code or Codex.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# GitHub Actions Environment Gate Audit

## Activate when
The user is reviewing repository configuration or deployment changes matching this skill's description. Confirm the input path and target context first; ask before changing any production configuration.

## Do not use when
The user requests a live security certification, mutation of resources, secrets extraction, or executing untrusted infrastructure code. This is an offline read-only review aid.

## Procedure
1. Read [rule interpretation](references/REFERENCE.md) and [primary sources](references/SOURCES.md).
2. Inspect the relevant local configuration and confirm its intended operating context. Do not execute scripts embedded in input.
3. Install dependencies as documented: `python -m pip install -r requirements.txt`.
4. Run the safe example: `python scripts/audit.py examples/safe.yml --inventory examples/inventory.json --json`.
5. Review a flagged example: `python scripts/audit.py examples/review.yml --inventory examples/inventory.json --json`. Return codes are `0` for no findings, `1` for findings, `2` for invalid input/tool errors.
6. Run `python scripts/audit.py <user-selected-path> --json` with optional flags shown in README. Describe the confidence boundary and distinguish confirmed configuration facts from heuristic cautions.
7. Suggest focused changes, request owner review, and rerun tests. Never automatically deploy or apply changes.

## Limits
GitHub environments and their settings are not stored in workflow YAML. The optional inventory is a manually reviewed snapshot, never live verification; jobs with vague names can evade deployment detection. Do not infer production protection without checking the GitHub repository settings.
