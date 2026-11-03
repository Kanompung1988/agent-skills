# Kubernetes PDB Scope Audit

**A safer review before workload disruption.** A portable, offline Python Agent Skill for inspecting `policy/v1` PodDisruptionBudget YAML and detecting selector-wide scope, conflicting budgets (from supplied Pod samples), malformed availability fields and uncertainty.

> [!NOTE]
> This is a review aid, not a live Kubernetes inspection, a drain rehearsal, or proof of availability.

[![CI](https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/workflows/ci.yml) · [Agent Skills specification](https://agentskills.io/specification) · MIT

## Install as a skill

**Claude Code:** `git clone https://github.com/Kanompung1988/k8s-pdb-scope-audit.git .claude/skills/k8s-pdb-scope-audit`  
**Codex:** `git clone https://github.com/Kanompung1988/k8s-pdb-scope-audit.git .agents/skills/k8s-pdb-scope-audit`

Install `PyYAML>=6,<7` in your trusted Python environment: `python -m pip install -r requirements.txt`.

## Quickstart

```bash
python audit.py examples/review.yaml --format json
python audit.py examples/safe.yaml
python -m unittest discover -s tests -v
```

`examples/review.yaml` intentionally returns exit **1** with `ALL_PODS`, `OVERLAP` and `ZERO_DISRUPTIONS`; `examples/safe.yaml` returns exit **0**. Invalid inputs return exit **2**. All fixture data is synthetic.

## Detection model

Input → PyYAML safe parsing → namespace-aware Pod / PDB selector evaluation → structured code/severity/object findings. A provided Pod document is needed to infer overlaps; workload templates and actual running pods are not included.

## Limits and security

Never calls Kubernetes or runs the manifests. It does not infer actual `disruptionsAllowed`, controller ownership, ReplicaSet selectors or user permissions. Missing Pods in an input are **not** evidence that an actual PDB matches nothing. No secrets, telemetry, or network calls. Treat alerts as human-review suggestions only.

## Contributing and license

Open an issue with a reproducible anonymized YAML fixture and expected finding; add unit tests for rule changes. CI runs Python 3.10/3.12. MIT License (see `LICENSE`). Author: AREA ZERO, 2026. Kubernetes behavior is documented at [Kubernetes upstream](https://kubernetes.io/docs/tasks/run-application/configure-pdb/); this project is not affiliated with Kubernetes.
