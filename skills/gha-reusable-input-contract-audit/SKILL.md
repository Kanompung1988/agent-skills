---
name: gha-reusable-input-contract-audit
description: Audit local GitHub Actions reusable workflow callers against on.workflow_call input and secret declarations. Use when reviewing local reusable workflow refactors, CI failures, missing inputs or secret handoffs; do not use for remote reusable workflow behavior or live GitHub settings.
license: MIT
compatibility: Python 3.10+ and PyYAML 6, offline; Claude Code and Codex compatible
---

# Reusable workflow input contract audit

1. Identify the repository's `.github/workflows` directory. Request a sanitized copy when workflows expose internal details.
2. Install `requirements.txt` into a local isolated environment. Do not execute any workflow.
3. Run `python scripts/audit.py .github/workflows --json`. Exit codes: 0 clean/review only, 2 error finding, 1 input failure.
4. Match each `code`, `file`, and `job` to the real caller/callee YAML and propose a minimal fix; never change workflow permissions or secrets without explicit approval.
5. Run again after changes. Use synthetic fixtures in `examples/`.

## Trigger guidance
Use for `jobs.<job>.uses: ./.github/workflows/*.yml` interface compatibility: required inputs, types of static literals, declared secrets and unknown fields.
Do not use for remote owner/repo workflow refs, nested expression evaluation, actual secret availability, GitHub API settings, or runtime permission checks.

Read [technical limitations](references/REFERENCE.md). No API calls, token reads or workflow execution.
