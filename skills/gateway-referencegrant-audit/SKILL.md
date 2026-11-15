---
name: gateway-referencegrant-audit
description: Audit rendered Kubernetes Gateway API HTTPRoute/GRPCRoute/TCPRoute/TLSRoute/UDPRoute backend references and Gateway TLS certificateRefs for missing cross-namespace ReferenceGrants. Use when reviewing ingress, shared backend or TLS namespace changes; offline static analysis of YAML only.
license: MIT
compatibility: Python 3.10+ and PyYAML 6; local rendered Gateway API YAML, no cluster credentials or network needed.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Gateway API ReferenceGrant trust-boundary audit

## Trigger
Use before deploying Gateway API route or TLS changes that reference targets in another namespace. Do **not** use to certify live controller behavior, mesh consumer policy, RBAC, AllowedRoutes or actual Service readiness.

## Workflow
1. Gather rendered Gateway API YAML and target-namespace ReferenceGrant YAML into one directory. Missing grants in incomplete input are **scope-sensitive** results.
2. Run `python -m pip install 'PyYAML>=6,<7'`, then `python scripts/audit.py examples/review.yaml --json` or pass your manifest directory. No kubeconfig or network is needed.
3. Review RG001 for absent grant, RG002 for empty grant policy, RG003 for malformed target group/kind, and RG004/RG005 for malformed cross-namespace refs.
4. Confirm that the grant belongs to the *target* namespace and its `from` group/kind/namespace and `to` group/kind/optional name match. Same-namespace backends do not need grants.
5. Manually check route attachment, mesh Service parentRef exceptions, controller feature support and resource existence before production rollout.
6. Run `python -m unittest discover -s tests -v` plus the safe/review fixtures; report finding counts, input scope and remaining uncertainty.

Exit 0 = no findings in supplied YAML; 1 = review findings; 2 = invalid input. See [rule reference](references/REFERENCE.md) and [official specifications](references/SOURCES.md).
