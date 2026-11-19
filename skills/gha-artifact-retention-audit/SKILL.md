---
name: gha-artifact-retention-audit
description: Review local GitHub Actions upload-artifact retention-days configuration for invalid periods, public/private caps, and supplied organization policy and minimum recovery windows. Use before updating artifact workflows or for repository hygiene; never accesses GitHub or secrets.
license: MIT
compatibility: Python 3.10 or newer; requires PyYAML; operates on local workflow YAML only
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# GitHub Actions Artifact Retention Audit

## Use when

- Reviewing workflow artifact retention windows before changes to `actions/upload-artifact`.
- Spotting retention periods longer than public/private policy caps or shorter than a team-required review window.
- Auditing local workflow files while keeping repository settings, private artifacts and token values offline.

**Do not use** this Skill to infer effective live GitHub policies, certify legal retention obligations, inspect artifacts, check a real repository's visibility, or decide whether a specific job ran. This tool cannot resolve expression values.

## Procedure

1. Select repository visibility (`--visibility public` or `private`) and obtain the effective retention ceiling from GitHub repository/organization settings, if available. Do not invent those values.
2. Run `python -m pip install -r requirements.txt` in this Skill's directory.
3. Audit local files: `python scripts/audit.py .github/workflows --visibility public --policy-days 60 --minimum-days 14 --format json`.
4. Review each `OUT_OF_RANGE_RETENTION`, `INVALID_RETENTION`, `EXCEEDS_SUPPLIED_POLICY` or `BELOW_REQUIRED_WINDOW` finding. `retention-days: 0` means use the repository default, **not** zero-day deletion.
5. Evaluate unresolved expressions and organizational overrides manually. Note that retention periods affect cost, availability, and compliance; ask a project owner before changing policy.
6. Re-run after any edits; optionally add `--strict` to return exit code `2` when findings are present.
7. Report local evidence with explicit policy assumptions; never claim a green scan proves historical artifacts remain available or that enterprise policy is satisfied.

## Reproducible fixtures

`python scripts/audit.py fixtures/safe.yml --visibility public --policy-days 90 --minimum-days 7 --strict`

`python scripts/audit.py fixtures/review.yml --visibility public --policy-days 60 --minimum-days 14 --format json --strict`

See [reference and limitations](references/REFERENCE.md).
