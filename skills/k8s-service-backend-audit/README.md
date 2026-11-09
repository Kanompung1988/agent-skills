<p align="center"><img src="assets/areazero-logo.svg" alt="Original AREAZERO brand mark" width="270"></p>

# Kubernetes Service Backend Audit

**Detect selectors that match no supplied backend template and named Service targetPorts missing from selected Pod declarations.**

[![Independent CI](https://github.com/Kanompung1988/k8s-service-backend-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/k8s-service-backend-audit/actions/workflows/ci.yml) · MIT · Python 3.10+

## The failure mode
Deployments roll out successfully but a Service selects the wrong labels, or expects a named port no matched container exposes. This bounded scanner cross-references supplied manifests in the same namespace, offering actionable finding codes without touching your cluster.

## Run

```bash
git clone https://github.com/Kanompung1988/k8s-service-backend-audit.git
cd k8s-service-backend-audit
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yaml --json
python scripts/audit.py examples/review.yaml --json
python -m unittest discover -s tests -v
```

Exit codes: 0 clean, 1 review, 2 invalid. No network, no Kubernetes credentials, no YAML execution or mutation. Findings on missing templates are **scope warnings**, not proof a live Service has no endpoints.

## Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Kanompung1988/k8s-service-backend-audit.git ~/.claude/skills/k8s-service-backend-audit
```

## Codex

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Kanompung1988/k8s-service-backend-audit.git ~/.agents/skills/k8s-service-backend-audit
```

## Evidence, known limits
Synthetic tests and fixture cases are executed in CI on Python 3.10 and 3.12. No live cluster or independent security audit is implied. Numeric targetPorts need not be in containerPort declarations; selectorless Services may be configured using manual EndpointSlices. No readiness or runtime checking. Official `skills-ref`: **NOT_RUN**, unless specifically proven elsewhere. See [rule notes](references/REFERENCE.md), [Kubernetes docs](references/SOURCES.md), and [MIT LICENSE](LICENSE). Original AREAZERO logo bytes preserved.
