---
name: compose-startup-readiness-audit
description: Diagnose Docker Compose depends_on ordering, readiness gates, missing healthchecks, invalid dependencies and cycles using local YAML only. Use before Compose deployments or when debugging intermittent first-start failures; not for live container inspection.
---

# Compose startup readiness audit

## Trigger
Use when a developer asks to review a local `compose.yaml`/`docker-compose.yml` for dependency readiness, startup ordering or `depends_on`/`healthcheck` mistakes. Do not use to certify runtime health, service connectivity or Docker security.

## Procedure
1. Identify the intended Compose YAML input. Never run `docker compose up`; this skill does not connect to Docker.
2. Inspect `references/rules.md` for supported semantics and review-only findings.
3. Install PyYAML: `python -m pip install 'PyYAML>=6,<7'` (Python 3.10+).
4. Execute `python scripts/audit.py compose.yaml --format json` from this skill's repository. Use `--strict` to fail CI for error-severity findings.
5. Review each reported `service`, `code` and `detail`; verify actual behavior using `docker compose config` separately only with explicit user permission.
6. Propose minimal changes and clearly label findings as static heuristics. Do not modify the input unless asked.

## Safety and scope
Read-only local files <=2MB, one document, YAML parsed with `safe_load_all`; no shell execution, networks, secrets, Docker socket or container runtime. This parser does not resolve Compose includes, extension fragments, profiles, variables, or multi-file merges. Treat missing readiness as a review finding, not proof of failure.

## Example
`python scripts/audit.py examples/review.yaml --strict` reports missing dependency, startup-not-ready and dependency-cycle findings and exits 1. `python scripts/audit.py examples/safe.yaml --strict` exits 0.
