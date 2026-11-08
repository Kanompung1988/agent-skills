---
name: k8s-vap-binding-audit
description: Audit local Kubernetes ValidatingAdmissionPolicy and ValidatingAdmissionPolicyBinding YAML together for missing references, ineffective enforcement actions, parameter resolution and fail-open policy choices. Use before Kubernetes admission changes; offline static review, not a cluster or CEL evaluator.
license: MIT
compatibility: Python 3.10+, PyYAML 6; offline rendered Kubernetes admissionregistration.k8s.io/v1 YAML input.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# ValidatingAdmissionPolicy binding contract audit

## When to use
Run on the rendered Kubernetes admission policy and binding manifests when reviewing a cluster admission-policy PR. Do not use this to assert the effective live cluster policy, test CEL, verify RBAC, or predict namespace/parameter selector resolution.

## Procedure
1. Gather ValidatingAdmissionPolicy and ValidatingAdmissionPolicyBinding v1 manifests for the intended deployment. Missing local policies/bindings are **scope warnings**, not proof that the cluster lacks them.
2. Run python scripts/audit.py PATH --json against a YAML file or a folder containing YAML files. Never send credentials or actual admission requests to a live cluster.
3. Inspect VP001–VP010, especially Warn/Audit-only actions, Deny+Warn, missing paramRef or missing parameterNotFoundAction, Ignore failurePolicy, and absent local policy references.
4. Manually verify the live parameter CRD/ConfigMap, RBAC read authorization, namespace matching, and CEL expressions before rollout. Kubernetes server version and defaults matter.
5. Run the unit tests plus safe/review fixtures. Document limitations and exact input scope when reporting.

Exit 0 = no static flags, 1 = flags found, 2 = bad or unsupported input. [Rules and limitations](references/REFERENCE.md) · [Kubernetes docs](references/SOURCES.md).
