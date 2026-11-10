---
name: gha-concurrency-scope-audit
description: Review local GitHub Actions YAML for cross-workflow case-insensitive concurrency group collisions, release cancellation hazards, and invalid queue settings. Use before modifying CI or deployment workflows, not for live GitHub queue state.
license: MIT
compatibility: Python 3.10+ and PyYAML 6. Offline local workflow analysis only.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# GitHub Actions Concurrency Scope Audit

## Use when
Reviewing multiple GitHub Actions workflows or release pipelines for unintended shared concurrency groups.

## Do not use for
Live Actions queue checks, expression resolution, protected environment verification, execution of workflows, or guarantees of deployment success.

## Steps
1. Gather all relevant local workflow files, preferably the complete `.github/workflows` directory.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Scan: `python scripts/audit.py .github/workflows --json`.
4. Review CC001–CC007 in [the rules](references/REFERENCE.md) and check whether shared groups and cancellation are intentional. Dynamic group expressions are not resolved.
5. Never automatically update production workflows solely based on a finding; request owner review.
6. Run `python -m unittest discover -s tests -v` and the safe and review fixtures.

Exit codes 0 clean, 1 findings, 2 input errors. Primary sources: [references](references/SOURCES.md).
