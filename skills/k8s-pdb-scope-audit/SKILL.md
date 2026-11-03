---
name: k8s-pdb-scope-audit
description: Audit local Kubernetes policy/v1 PodDisruptionBudget YAML for wide or null selectors, overlapping Pod matches, and malformed availability fields before deployment. Use during Kubernetes manifests review, upgrades and drain planning; not for real-time eviction or cluster health verification.
license: MIT
compatibility: Python 3.10+ with PyYAML 6; offline and read-only.
metadata:
  author: AREA ZERO
  version: "1.0.0"
---

# Kubernetes PDB Scope Audit

Use for code review of untrusted *local* Kubernetes YAML/JSON; never imply this is a live-cluster decision. Ask for the manifest path, use read-only inspection, and explain the difference between configuration and observed availability.

1. Run `python -m pip install -r requirements.txt` only in a trusted environment; do not auto-install packages while evaluating untrusted workspaces.
2. Run `python audit.py path/to/manifests.yaml --format json` from the skill directory (exit 0 = no warning/error; 1 = review needed; 2 = invalid input). The script never calls kubectl.
3. Review `ALL_PODS`, `NULL_SELECTOR`, `OVERLAP`, `BUDGET_FIELDS`, and `ZERO_DISRUPTIONS` in context; inspect actual workload selectors, controller replicas and PDB status separately.
4. Report each finding, exact manifest object, recommended review, and uncertainty. Do **not** recommend automatic modifications or assert drain safety.
5. Run `python -m unittest discover -s tests -v` if changing detection logic.

Use [references/BEHAVIOR.md](references/BEHAVIOR.md) to understand explicit limitations. Do not use for admission policy enforcement, installed cluster scans or deployment management.
