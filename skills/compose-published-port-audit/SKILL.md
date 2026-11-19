---
name: compose-published-port-audit
description: Review local Docker Compose YAML to identify published ports that bind wildcard, non-loopback, or implicit host interfaces. Use during Docker Compose exposure reviews before local development or deployment. Never changes containers or firewall rules.
license: MIT
compatibility: Python 3.10 or newer and PyYAML 6.0.3; runs offline with no Docker daemon
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Compose Published Port Audit

## Use when

- A developer asks whether `ports:` entries may be accessible from other hosts.
- Comparing explicitly loopback-bound ports with unspecified or wildcard host IPs.
- Reviewing a Compose file before it is deployed; safe to run without Docker.

**Do not use** to claim a service is reachable from the internet, evaluate real firewalls/daemon defaults, or review Swarm/overlay deployment. `expose:` alone does not publish a host port.

## Procedure

1. Obtain the Compose YAML and confirm permission to inspect it. Never require secret files or `.env` values.
2. Run `python -m pip install -r requirements.txt` from the skill root.
3. Run `python scripts/audit.py /path/to/compose.yaml --format json` (add `--strict` to return code 2 on findings).
4. Separate **high** (`0.0.0.0` / `::` explicitly) from **review** (default binding, non-loopback, unresolved interpolation, host network).
5. Before remediation, check Docker Engine/Compose versions, daemon/network bind-address defaults, host firewall, and intended service access. Recommend loopback host IP only when local-only access is desired.
6. Report exact service and `ports` entry index, code, and why it needs review; never say the tool proved public reachability.

See [reference and limits](references/REFERENCE.md). Compare `fixtures/safe.yaml` and `fixtures/review.yaml` for synthetic demos.
