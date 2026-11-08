<p align="center"><img src="assets/areazero-logo.svg" alt="AREA ZERO — AI SOFTWARE HOUSE" width="280"></p>

# GitHub Actions Artifact Attestation Gate Audit

**Offline workflow review: signer scope, effective permission declarations, and fail-open verification.**

[![Independent CI](https://github.com/Kanompung1988/gha-attestation-gate-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/gha-attestation-gate-audit/actions/workflows/ci.yml) · MIT · Python 3.10+

## Why

An attestation is only useful when consumers verify the correct artifact and enforce the result. A workflow can generate provenance correctly but omit required permissions or perform a verify command that cannot fail the job.

This standalone Agent Skill performs a narrow, *read-only static review* of local GitHub Actions YAML. It reports concrete AA001–AA009 diagnostic codes and structured JSON without echoing run scripts, tokens or environment values. **It does not verify any actual attestation or claim release integrity.**

## Quick start

    git clone https://github.com/Kanompung1988/gha-attestation-gate-audit.git
    cd gha-attestation-gate-audit
    python -m pip install 'PyYAML>=6,<7'
    python scripts/audit.py examples/safe.yml --json
    python scripts/audit.py examples/review.yml --json

Use a single workflow file or a directory: python scripts/audit.py .github/workflows --json

Exit codes: 0 = no diagnostics; 1 = review findings; 2 = malformed/unsafe input. JSON contains rule identifiers, job name, filename and non-secret human guidance.

## Install with Claude Code or Codex

**Claude Code:** place the *entire repository* into ~/.claude/skills/gha-attestation-gate-audit/ with SKILL.md at that path root. For example:

    mkdir -p ~/.claude/skills
    git clone https://github.com/Kanompung1988/gha-attestation-gate-audit.git ~/.claude/skills/gha-attestation-gate-audit

**Codex:** place the whole repository into ~/.agents/skills/gha-attestation-gate-audit/:

    mkdir -p ~/.agents/skills
    git clone https://github.com/Kanompung1988/gha-attestation-gate-audit.git ~/.agents/skills/gha-attestation-gate-audit

Reload skill discovery if required. This follows https://agentskills.io/specification.

## Tests and boundaries

    python -m unittest discover -s tests -v
    python scripts/audit.py examples/safe.yml --json
    python scripts/audit.py examples/review.yml --json

CI runs unit tests plus both fixtures on Python 3.10 and 3.12. **Official skills-ref validator: NOT_RUN unless independently evidenced.** The heuristic has false positives and blind spots; never use a clean report as signature verification, provenance validation, production security certification, or a substitute for gh attestation verify. Full rule explanations: [reference](references/REFERENCE.md); [primary sources](references/SOURCES.md).

Original AREAZERO SVG is reused without modification from the owner's public brand asset. Contributions and reproducible bug reports welcome. License: [MIT](LICENSE).
