---
name: compose-profile-dependency-audit
description: Catch dependencies excluded by Compose profile selections before your stack fails to start. Use when reviewing Docker Compose profiles and dependency routing.
license: MIT
compatibility: Python 3.10 or newer and PyYAML 6.x; read-only offline CLI; compatible with Claude Code and Codex.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Docker Compose Profile Dependency Audit

## Trigger

Use this skill when a developer asks to validate Docker Compose stacks with `profiles`, `depends_on`, service namespace references (`network_mode`, `pid`, `ipc`), `links`, and local `extends`.

**Do not trigger:** Do not use as a multi-file Compose merge resolver, runtime health check, validation of all Compose keys, or confirmation that a user will ever activate a given profile. For actual effective model use `docker compose config --profiles ...` in your own environment.

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
