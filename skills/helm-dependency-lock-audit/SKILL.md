---
name: helm-dependency-lock-audit
description: Identify missing Chart.lock, dependency identity drift, unexpected locked entries and exact version mismatch before Helm chart delivery. Use before reviewing changes to Helm Chart.yaml and Chart.lock files in chart directories; offline read-only validation of local files.
license: MIT
compatibility: Python 3.10+; PyYAML 6.x; local inputs, no credentials or network required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Helm Dependency Lock Audit

## Trigger
Run on Helm Chart.yaml and Chart.lock files in chart directories when asked to identify drift or hidden operational risks. Do not run for unrelated requests; do not claim live-cluster or registry validation.

## Procedure
1. Collect the relevant local YAML files. Do not include credentials or private manifests unless approved.
2. Install PyYAML: `python -m pip install 'PyYAML>=6,<7'`.
3. Execute `python scripts/audit.py examples/safe --json` for a clean example, `python scripts/audit.py examples/review --json` for a review example, or `python scripts/audit.py PATH --json`.
4. Read each finding's rule, file, resource, and remediation; verify the risk against the project's real deployment workflow.
5. Distinguish observed configuration issues from unknown cluster/Helm state. Never edit files automatically.
6. Re-run tests with `python -m unittest discover -s tests -v` after edits.

Exit 0 = no findings in input scope; 1 = findings; 2 = invalid input. No remote calls or artifact execution.
See [rule reference](references/RULES.md) and [primary sources](references/SOURCES.md).
