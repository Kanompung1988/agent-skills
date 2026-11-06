---
name: compose-mount-write-audit
description: Review local Docker Compose YAML for writable host bind mounts, Docker socket exposure, sensitive target paths and unresolved mount syntax. Use before deployment when assessing Compose volumes and read_only behavior; not for live runtime scans.
license: MIT
compatibility: Python 3.10+ and PyYAML 6.x; local offline files.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Compose Mount Write Audit

## Activate
Use for review of authorized Compose YAML, bind mount writes, Docker socket mounts or `read_only` setting confusion. Do **not** use as a live Docker, Docker security certification or full Compose configuration validator.

## Steps
1. Read [rules and scope](references/RULES.md). Never automatically read environment files or secrets.
2. Install `python -m pip install -r requirements.txt`.
3. Test `python scripts/audit.py examples/safe.yml --json` (0) and `python scripts/audit.py examples/review.yml --json` (1).
4. Run `python scripts/audit.py /path/to/compose.yaml --json`.
5. Interpret 0=no modeled findings, 1=review, 2=invalid file. Cite exact rule IDs. Explain that container root `read_only` does not make host binds read-only, and a read-only Docker socket bind does not remove Docker API authority.
6. Suggest minimally scoped changes and separate operator-run `docker compose config` plus staging verification; never auto-deploy or modify files.

Single-file offline static analysis only. No shell, Docker client, networking, environment interpolation or full risk guarantee.
