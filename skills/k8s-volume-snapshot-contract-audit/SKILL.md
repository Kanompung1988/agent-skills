---
name: k8s-volume-snapshot-contract-audit
description: "Review local Kubernetes CSI snapshot YAML for VolumeSnapshotClass defaults, deletion policies, VolumeSnapshotContent bindings and PVC restore sources or volume mode mismatch. Use before backups and snapshot or restore rollout changes."
license: MIT
compatibility: "Python 3.10+ and PyYAML 6.x; offline, no kubeconfig or cluster access."
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes CSI Snapshot Contracts

Activate for VolumeSnapshot, VolumeSnapshotContent, VolumeSnapshotClass and PersistentVolumeClaim restore YAML review. Do not activate to certify live CSI functionality, backup success or recovery.

1. Collect authorized local YAML manifests. Do not read cluster secrets or execute kubectl.
2. Read [technical boundaries](references/REFERENCE.md), especially that references can exist outside the submitted batch.
3. Run `python audit.py examples/safe.yaml` for a clean smoke, then `python audit.py path/to/manifests --format json --strict`.
4. Classify `error` as concrete local contradiction; `review` requires manual inspection. Exit codes: 0=no errors, 2=errors or review with strict, 1=input failures.
5. Explain observed objects, finding codes, proposed safe next checks and explicit limits. Never delete a backing CSI snapshot or change configuration without permission.
