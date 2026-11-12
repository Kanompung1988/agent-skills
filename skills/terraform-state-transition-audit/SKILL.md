---
name: terraform-state-transition-audit
description: Review Terraform moved and removed HCL blocks for conflicting moves, cycles, duplicated targets and state handoffs missing destroy=false. Use when reviewing Terraform refactors or resource retirement pull requests before terraform plan and apply.
license: MIT
compatibility: Python 3.10+ standard library only; offline, read-only; Claude Code or Codex.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Terraform State Transition Audit

## Activate when
The user is reviewing repository configuration or deployment changes matching this skill's description. Confirm the input path and target context first; ask before changing any production configuration.

## Do not use when
The user requests a live security certification, mutation of resources, secrets extraction, or executing untrusted infrastructure code. This is an offline read-only review aid.

## Procedure
1. Read [rule interpretation](references/REFERENCE.md) and [primary sources](references/SOURCES.md).
2. Inspect the relevant local configuration and confirm its intended operating context. Do not execute scripts embedded in input.
3. Install dependencies as documented: `python --version`.
4. Run the safe example: `python scripts/audit.py examples/safe.tf --json`.
5. Review a flagged example: `python scripts/audit.py examples/review.tf --json`. Return codes are `0` for no findings, `1` for findings, `2` for invalid input/tool errors.
6. Run `python scripts/audit.py <user-selected-path> --json` with optional flags shown in README. Describe the confidence boundary and distinguish confirmed configuration facts from heuristic cautions.
7. Suggest focused changes, request owner review, and rerun tests. Never automatically deploy or apply changes.

## Limits
This lightweight lexical reviewer is not an HCL parser, Terraform plan, or state interpreter. It supports simple static resource/module addresses. Unknown/dynamic addresses are manual-review findings, not proven errors. Never apply Terraform solely on this audit; validate and review an actual plan against the target workspace.
