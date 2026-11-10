---
name: buildkit-secret-boundary-audit
description: Scan local Dockerfiles for secret-like ARG/ENV declarations, suspicious credential COPY/ADD paths, unsafe RUN variable use without BuildKit secret mounts, and optional secret mounts. Use during container build review, not for image security certification.
license: MIT
compatibility: Python 3.10+ standard library. Offline Dockerfiles; no Docker daemon.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# BuildKit Secret Boundary Audit

## Use when
A developer asks to review Dockerfiles for build-time credential leakage risks before deploying build pipelines.

## Do not use
To inspect image layers, check actual secrets, audit Docker Compose build contexts, verify external build commands, or certify production container safety.

## Procedure
1. Gather the intended Dockerfiles from the repository.
2. Run `python scripts/audit.py Dockerfile --json`, or scan a directory recursively.
3. Inspect BK001–BK007 in [the rule reference](references/REFERENCE.md). Names and paths are heuristics; no secret values are printed.
4. Prefer BuildKit `RUN --mount=type=secret` over ARG/ENV for credentials, and consult [official sources](references/SOURCES.md).
5. Verify the build invocation, secret provisioners, .dockerignore and CI setup manually; never automatically change credentials or publish findings containing secrets.
6. Run `python -m unittest discover -s tests -v` plus safe/review examples.

Exit 0 clean, 1 review findings, 2 invalid input. No Docker daemon, network calls, or mutations.
