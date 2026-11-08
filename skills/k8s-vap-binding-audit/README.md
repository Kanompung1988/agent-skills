<p align="center"><img src="assets/areazero-logo.svg" alt="AREA ZERO — AI SOFTWARE HOUSE" width="280"></p>

# Kubernetes ValidatingAdmissionPolicy Binding Audit

**Review relationships, actions and fail-open parameter decisions before deploying admission policies.**

[![Independent CI](https://github.com/Kanompung1988/k8s-vap-binding-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/k8s-vap-binding-audit/actions/workflows/ci.yml) · MIT · Python 3.10+

## Problem

A ValidatingAdmissionPolicy without a binding does not enforce anything. A binding may only warn/audit, reference a policy not supplied alongside it, or allow absent parameters. These are easy to miss when reviewing distributed Kubernetes YAML.

This Agent Skill performs **bounded offline static review** of admissionregistration.k8s.io/v1 YAML. It never contacts Kubernetes, evaluates CEL, changes policies, or reads credentials. Report codes VP001–VP014 explain what needs a human review; some are *intentional choices*, not bugs.

## Quick start

    git clone https://github.com/Kanompung1988/k8s-vap-binding-audit.git
    cd k8s-vap-binding-audit
    python -m pip install 'PyYAML>=6,<7'
    python scripts/audit.py examples/safe.yaml --json
    python scripts/audit.py examples/review.yaml --json

Use a single rendered multi-document YAML file or a directory of manifests. Exit codes: 0 = clean static checks; 1 = review findings; 2 = invalid input.

## Install in Claude Code / Codex

**Claude Code:** clone the whole repository to ~/.claude/skills/k8s-vap-binding-audit/ so SKILL.md is at the root:

    mkdir -p ~/.claude/skills
    git clone https://github.com/Kanompung1988/k8s-vap-binding-audit.git ~/.claude/skills/k8s-vap-binding-audit

**Codex:** clone the whole repository to ~/.agents/skills/k8s-vap-binding-audit/:

    mkdir -p ~/.agents/skills
    git clone https://github.com/Kanompung1988/k8s-vap-binding-audit.git ~/.agents/skills/k8s-vap-binding-audit

See https://agentskills.io/specification and reload skill discovery when needed.

## Quality and limitations

    python -m unittest discover -s tests -v
    python scripts/audit.py examples/safe.yaml --json
    python scripts/audit.py examples/review.yaml --json

GitHub Actions independently runs real unit tests and fixture smoke on Python 3.10 / 3.12. Synthetic cases do not prove completeness, cluster safety or Kubernetes server acceptance. **Official skills-ref validator: NOT_RUN** unless a passing invocation is recorded. See [reference](references/REFERENCE.md) and [sources](references/SOURCES.md).

Source code, tests, issue discussion and PRs are public. Original AREAZERO brand SVG preserved unchanged. MIT [LICENSE](LICENSE).
