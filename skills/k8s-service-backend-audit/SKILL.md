---
name: k8s-service-backend-audit
description: Check Kubernetes Service selectors against supplied Pod/workload template labels and confirm named targetPorts are declared on selected backends. Use in pre-deploy YAML review; offline static analyzer, not live EndpointSlice validation.
license: MIT
compatibility: Python 3.10+, PyYAML 6, rendered Kubernetes YAML and no cluster access.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes Service Backend Audit

## Trigger and non-trigger
Use with rendered Services and companion Deployments, Pods, StatefulSets, DaemonSets, ReplicaSets, Jobs or CronJobs before applying manifests. Do NOT use to certify runtime reachability, readiness, manual EndpointSlices, DNS or ingress connectivity.

## Procedure
1. Gather Service YAML and all expected same-namespace backend workload manifests in a file or directory.
2. Install `python -m pip install -r requirements.txt` then run `python scripts/audit.py PATH --json`.
3. Examine SV001–SV004. A missing local backend is only a scope warning. Selectorless and ExternalName Services are valid and skipped.
4. Verify real EndpointSlices, readiness and targetPort configuration with authorized cluster access separately. Never automatically change manifests based solely on a finding.
5. Run unit tests and both fixture CLI examples, then record scope and any limitations.

Exit 0 no findings, 1 findings, 2 invalid input. [Rule notes](references/REFERENCE.md) · [Kubernetes source](references/SOURCES.md).
