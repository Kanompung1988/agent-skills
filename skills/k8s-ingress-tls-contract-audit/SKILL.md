---
name: k8s-ingress-tls-contract-audit
description: Review local Kubernetes networking.k8s.io/v1 Ingress TLS host and same-namespace Secret metadata contracts. Use when checking TLS migration manifests, host drift, or certificate Secret key declarations; not for controller runtime validation or real certificate trust/expiry.
license: MIT
compatibility: Python 3.10+ and PyYAML 6, offline; Claude Code and Codex compatible
---

# Ingress TLS contract audit

1. Work only on synthetic or sanitized Kubernetes YAML; do not copy real TLS private key material into this skill or agent context.
2. Install `requirements.txt`, then run `python scripts/audit.py examples/safe.yaml --json`.
3. Audit manifests via `python scripts/audit.py path/to/sanitized-manifests --json`. The tool inspects only Secret type and key *names*, and does not print values.
4. Distinguish a missing Secret in this batch (review, not cluster absence) from an incorrect Secret present in the batch (error).
5. Propose small YAML fixes; do not apply resources or disclose certificate contents. Re-run before considering a change.

## Trigger guidance
Use for host/rule mismatch, TLS Secret naming, types and mandatory `tls.crt` / `tls.key` keys.
Do not use for controller-specific TLS behavior, certificate chain checks, expiration, runtime handshake, backend routing or cluster health.

See [reference and boundaries](references/REFERENCE.md). Exit codes: 0 no errors, 2 errors, 1 invalid inputs.
