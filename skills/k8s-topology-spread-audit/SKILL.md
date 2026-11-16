---
name: k8s-topology-spread-audit
description: "Find risky topologySpreadConstraints: invalid minDomains/maxSkew, missing or mismatched self-selectors, matchLabelKeys conflicts and node inclusion policies. Use before reviewing changes to Kubernetes Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet, Job and CronJob pod templates; offline read-only validation of local files."
license: MIT
compatibility: Python 3.10+; PyYAML 6.x; local inputs, no credentials or network required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes Topology Spread Audit

## Trigger
Run on Kubernetes Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet, Job and CronJob pod templates when asked to identify drift or hidden operational risks. Do not run for unrelated requests; do not claim live-cluster or registry validation.

## Procedure
1. Collect the relevant local YAML files. Do not include credentials or private manifests unless approved.
2. Install PyYAML: `python -m pip install 'PyYAML>=6,<7'`.
3. Execute `python scripts/audit.py examples/safe.yaml --json` for a clean example, `python scripts/audit.py examples/review.yaml --json` for a review example, or `python scripts/audit.py PATH --json`.
4. Read each finding's rule, file, resource, and remediation; verify the risk against the project's real deployment workflow.
5. Distinguish observed configuration issues from unknown cluster/Helm state. Never edit files automatically.
6. Re-run tests with `python -m unittest discover -s tests -v` after edits.

Exit 0 = no findings in input scope; 1 = findings; 2 = invalid input. No remote calls or artifact execution.
See [rule reference](references/RULES.md) and [primary sources](references/SOURCES.md).
