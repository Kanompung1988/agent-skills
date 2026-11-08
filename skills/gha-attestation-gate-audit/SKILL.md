---
name: gha-attestation-gate-audit
description: Inspect GitHub Actions workflow YAML for artifact attestation creation permissions, signer/subject metadata and fail-open consumer verification gates. Use in CI provenance and release PR reviews; offline static diagnostics, not cryptographic attestation verification.
license: MIT
compatibility: Python 3.10+ with PyYAML 6; no GitHub credentials, remote access or workflow execution.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# GitHub Actions attestation gate audit

## When to use
Use before approving a GitHub Actions pipeline that creates or consumes build artifact attestations, especially with actions/attest and gh attestation verify. Do not use to verify actual signatures, trusted roots, artifact digests, repository identity, or execution order across separate workflows.

## Agent procedure
1. Locate the real workflow YAML files under .github/workflows; run against those local files only.
2. Run python scripts/audit.py PATH --json for a single YAML file or workflow directory.
3. Review AA001–AA008 with the human owner. These are conservative source-code review prompts, not authoritative runtime verdicts.
4. For release consumers, insist on an actual gh attestation verify run with repository/signer constraints and a failing exit status before deploying. Validate provenance with GitHub CLI, not this scanner.
5. Run synthetic fixtures and tests before advising changes. Do not echo credentials, environment values, or the text of a workflow run step to reports.
6. Do not modify files unless explicitly asked; never execute downloaded artifacts as part of this audit.

## Example
python -m pip install 'PyYAML>=6,<7'
python scripts/audit.py examples/safe.yml --json
python scripts/audit.py examples/review.yml --json

Exit 0 means no *known static rules* triggered; 1 means at least one finding; 2 means invalid input. See [rule boundaries](references/REFERENCE.md) and [GitHub documentation](references/SOURCES.md).
