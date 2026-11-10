---
name: docker-build-secret-boundary-audit
description: Audit Dockerfiles offline for sensitive-looking ARG/ENV variables, BuildKit RUN secret mount scoping, optional mounts, and same-instruction secret access mistakes. Use before image builds; not a live leak scanner.
license: MIT
compatibility: Python 3.10+ standard library; no Docker daemon required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Docker BuildKit secret boundary audit

Use during authorized pre-build Dockerfile review. Do not run Docker or interpret the result as proof that no image layer leaks secrets.

1. Identify intended Dockerfile and avoid copying secrets into audit reports.
2. Run `python scripts/audit.py Dockerfile --json` (no dependencies required).
3. Interpret BS001–BS007 using `references/REFERENCE.md`: review ARG/ENV credential persistence; check RUN-local mounts and required flags.
4. Verify with `docker build --check` and trusted platform/build settings separately; do not silently rewrite files.
5. Run `python -m unittest discover -s tests -v` and both examples before suggesting fixes.

Exit 0 no static findings, 1 review, 2 invalid input. Never execute target commands.
