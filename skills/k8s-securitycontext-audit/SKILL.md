---
name: k8s-securitycontext-audit
description: Review rendered Kubernetes Pod and workload securityContext effective settings, capabilities, seccomp, non-root defaults and host namespace hazards. Use before deployment or when reviewing Kubernetes YAML; never requires cluster credentials.
license: MIT
compatibility: Requires Python 3.10 or later and PyYAML 6.x; offline, local-input read-only.
metadata:
  author: AREAZERO
  version: "1.0.0"
---

# Kubernetes securityContext audit

## Use when
- A developer or agent asks to inspect rendered Kubernetes workload manifests before applying them.
- You can read local inputs and present specific, actionable review findings.

## Do not use when
- The user needs a definitive Pod Security Standards admission pass/fail or live cluster inspection.
- Source input is missing, or analysis would require executing untrusted code, changing Git state or performing network operations.

## Procedure
1. Ask for or locate the relevant local rendered YAML (not Helm template).
2. Read [reference boundaries](references/REFERENCE.md) and explain that this is offline advisory analysis.
3. Run `python scripts/audit.py examples/safe.yaml --json`. JSON output is safe for automated parsing; code 0 = no findings, 1 = review findings, 2 = input error.
4. Report the code, affected resource/path, severity, and a minimal suggested change. Never assert complete security or runtime state.
5. Do **not** automatically edit deployment files, fetch submodules or deploy workloads. Request explicit authorization for modifications.

## Edge cases
- Multi-document YAML, Kubernetes List, Pod templates, init and ephemeral containers, Windows vs Linux fields are handled. Unsupported resource kinds are ignored.
- Never expose secrets from source; findings contain only normalized rules, resource names and paths.
