---
name: k8s-psa-namespace-audit
description: Review namespace Pod Security Admission levels and version pins before deployment. Use when reviewing Kubernetes Namespace Pod Security Admission labels before deployment.
license: MIT
compatibility: Python 3.10 or newer and PyYAML 6.x; read-only offline CLI; compatible with Claude Code and Codex.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes Pod Security Admission Namespace Audit

## Trigger

Use this skill when a developer asks to validate Kubernetes Namespace YAML and desired Pod Security Admission label policy, especially before changing `enforce`, `warn`, or `audit` labels.

**Do not trigger:** Do not use as a live Pod Security Admission evaluation, Pod Security Standards implementation, admission-controller configuration inspector, or proof of policy enforcement. Default admission policies and exemptions must be obtained from cluster operators.

## Procedure

1. Identify the single local, user-authorized input file. Do not open unrelated paths. This tool does not run infrastructure commands.
2. Install Python dependency from `requirements.txt` in a private or disposable environment: `python -m pip install -r requirements.txt`.
3. Run `python scripts/audit.py <input.yaml> --format json`. Use `--format json` for machine-readable findings.
4. Interpret exit codes strictly: **0** no findings in reviewed scope, **2** review findings, **1** invalid input/CLI error. Do not claim `0` proves production safety.
5. For demonstrations, run `python scripts/audit.py fixtures/safe.yaml --format json` and `python scripts/audit.py fixtures/review.yaml --format json` and compare JSON `rule`, `message`, and scenario/namespace to the source.
6. Suggest a minimal change **without applying it**. Report unsupported constructs and request human verification before deployments.
7. State evidence boundaries from [Technical reference](references/REFERENCE.md) and the official documentation.

## Safety and non-goals

- Parse local YAML safely; never evaluate templates, environment substitutions, shell commands, Kubernetes API calls, Docker Compose commands or secrets.
- Review service/namespace identifiers and metadata only. Do not expose unrelated source file contents in reports.
- Treat findings as review leads, not proof that runtime behavior is insecure or broken.

## Examples

```bash
python scripts/audit.py fixtures/safe.yaml --format json
python scripts/audit.py fixtures/review.yaml --format json
python -m unittest discover -s tests -v
```

See [README](README.md) for installation into Claude Code/Codex and [Technical reference](references/REFERENCE.md) for rule boundaries.
