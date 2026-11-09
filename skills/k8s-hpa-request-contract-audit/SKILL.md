---
name: k8s-hpa-request-contract-audit
description: Check autoscaling/v2 HorizontalPodAutoscalers against supplied Kubernetes workloads for absent CPU/memory utilization requests, duplicate scaling targets and invalid replicas. Use during pre-deploy YAML review, not as a live cluster checker.
license: MIT
compatibility: Python 3.10+, PyYAML 6, offline rendered Kubernetes YAML.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes HPA Request Contract Audit

## When to use
Before Kubernetes deployment changes, review a full set of rendered autoscaling/v2 HPA and workload manifests. Do not use for live cluster guarantees, custom metrics, or controller operational behavior.

## Workflow
1. Gather all intended HPA and Deployment, StatefulSet, DaemonSet or ReplicaSet YAML into one file or directory.
2. Run `python -m pip install -r requirements.txt` then `python scripts/audit.py PATH --json`. No network or credentials required.
3. Review HP000–HP007 findings; absent companion manifests are scope warnings, not proof of a missing live workload.
4. Verify resource requests on all relevant containers and confirm actual cluster configuration manually before acting.
5. Run `python -m unittest discover -s tests -v` and both example fixtures; report actual input scope.

Exit 0 = clean static checks, 1 = review findings, 2 = invalid input. See [rules](references/REFERENCE.md) and [sources](references/SOURCES.md).
