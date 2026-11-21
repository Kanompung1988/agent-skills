---
name: k8s-runtimeclass-contract-audit
description: Audit Kubernetes RuntimeClass and Pod manifests for runtimeClassName references, merged nodeSelector conflicts, handler and scheduling shape, and Pod overhead quantities. Use when reviewing RuntimeClass, gVisor, Kata Containers, Pod scheduling, or runtime overhead YAML before deployment.
license: MIT
compatibility: Python 3.10+ and PyYAML 6.x; offline read-only YAML CLI; no cluster access required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes RuntimeClass Contract Audit

## Trigger
Use when reviewing local Kubernetes `RuntimeClass` definitions and Pods or workload templates that set `runtimeClassName`, especially when runtime-specific node labels, taints, or Pod overhead are involved.

Do not use for live cluster capability checks, admission-server validation, runtime handler installation, node inventory, CNI checks, or proof that a runtime is operational.

## Procedure
1. Identify only the user-authorized YAML files or directory. Never read unrelated paths.
2. Install the single parser dependency in a disposable environment: `python -m pip install -r requirements.txt`.
3. Run `python scripts/audit.py <path-or-directory> --format json`.
4. Review `RUNTIMECLASS_NODESELECTOR_CONFLICT` first. Kubernetes merges RuntimeClass and Pod node selectors; conflicting values cause admission rejection. RuntimeClass tolerations are appended to Pod tolerations, not intersected.
5. Review invalid handler, selector, toleration, and `overhead.podFixed` findings. Quantity validation is conservative and does not replace API-server schema validation.
6. Treat `RUNTIMECLASS_EXTERNAL_REFERENCE` as informational: the class may exist outside the supplied files. Ask for the relevant RuntimeClass manifest before concluding it is missing.
7. Propose a minimal patch but do not edit or apply manifests unless explicitly authorized. Never run `kubectl`, contact a cluster, or infer node availability.
8. State the static-analysis boundary and link the official references in `references/REFERENCE.md`.

## Exit codes
- `0`: no findings at the configured threshold in the supplied files; not proof of cluster safety.
- `2`: one or more findings at the configured threshold.
- `1`: invalid invocation or no YAML files.

## Examples
```bash
python scripts/audit.py fixtures/safe.yaml --format json
python scripts/audit.py fixtures/review.yaml --format json
python -m unittest discover -s tests -v
```
