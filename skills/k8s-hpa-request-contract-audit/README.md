<p align="center"><img src="assets/areazero-logo.svg" alt="AREAZERO original brand logo" width="270"></p>

# Kubernetes HPA Request Contract Audit

**Catch autoscalers that cannot calculate resource Utilization because their workload is missing CPU or memory requests.**

[![Independent CI](https://github.com/Kanompung1988/k8s-hpa-request-contract-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/k8s-hpa-request-contract-audit/actions/workflows/ci.yml) · MIT · Python 3.10+

## Problem and scope
Sidecar containers and missing resource requests can make HPA resource utilization undefined. The offline checker cross-references supplied autoscaling/v2 HPA manifests with workload Pod templates to flag missing requests, duplicate targets and inconsistent replica bounds. Input may be partial; results are suggestions for human verification, not evidence of live cluster failure.

## Run locally

```bash
git clone https://github.com/Kanompung1988/k8s-hpa-request-contract-audit.git
cd k8s-hpa-request-contract-audit
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yaml --json
python scripts/audit.py examples/review.yaml --json
python -m unittest discover -s tests -v
```

Exit 0 = no findings, 1 = review, 2 = invalid input. Files/directory accepted. No execution of supplied YAML.

## Install for Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Kanompung1988/k8s-hpa-request-contract-audit.git ~/.claude/skills/k8s-hpa-request-contract-audit
```

## Install for Codex

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Kanompung1988/k8s-hpa-request-contract-audit.git ~/.agents/skills/k8s-hpa-request-contract-audit
```

## Boundaries
Static, offline, read-only, synthetic tests. No claims of production completeness or independent review. Python 3.10 and 3.12 jobs must pass on real GitHub CI. Official `skills-ref`: **NOT_RUN** unless separately documented. [Rules](references/REFERENCE.md) · [Sources](references/SOURCES.md) · [MIT LICENSE](LICENSE). Authentic AREA ZERO logo bytes are preserved from existing Skill Lab asset.
