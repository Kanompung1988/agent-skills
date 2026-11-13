---
name: gha-cache-mode-boundary-audit
description: Review GitHub Actions cache-mode for potentially untrusted triggers, workflow/job overrides, dynamic values and disabled cache steps. Use during CI cache security review before merging workflow YAML; no network access.
license: MIT
compatibility: Requires Python 3.10+ and PyYAML 6.x; offline local file access.
metadata:
  author: AREAZERO
  version: "1.0.0"
---

# GitHub Actions Cache Mode Boundary Audit

Use this skill **when** the user asks for relevant pre-deployment or pre-merge configuration review. Do **not** use it to claim a live system is secure, run arbitrary workflow code, access secrets, or modify source.

## Procedure
1. Identify an explicitly supplied local YAML path and confirm it is intended for review.
2. Install the declared dependency in an approved Python environment: `python -m pip install -r requirements.txt`.
3. Run `python scripts/audit.py PATH --json`. Exit 0 means clean under implemented rules, 1 means review findings, 2 means parse/input error.
4. Explain each finding with its rule ID. Consult [the rule reference](references/REFERENCE.md) and [primary documentation](references/SOURCES.md).
5. Discuss deployment consequences and ask for human review before any change. Never mutate YAML or execute the workload.
6. Disclose limitations: this static analysis does not check live platform state, credentials or effective runtime behavior.

## Demos
- `python scripts/audit.py examples/safe.yaml --json` is expected to exit 0.
- `python scripts/audit.py examples/review.yaml --json` is expected to exit 1.

No network calls, no shell evaluation, no input writes, and per-file size limited to 2 MiB.
