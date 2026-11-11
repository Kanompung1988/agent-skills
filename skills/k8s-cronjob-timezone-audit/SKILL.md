---
name: k8s-cronjob-timezone-audit
description: Review Kubernetes CronJob YAML for time zones, daylight-saving shifts, short starting deadlines, concurrency replacement and missed-run hazards. Use before deploying batch schedules.
license: MIT
compatibility: Python 3.10+ with PyYAML; offline and read-only; Claude Code and Codex.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes CronJob Timezone & Schedule Audit

## Use this skill when
A developer asks to review relevant Kubernetes/Argo CD YAML for configuration hazards before pull request review, upgrade, or deployment.

## Do not use for
Live cluster checks, runtime behavior guarantees, automatic manifest modification, secret discovery, or untrusted code execution.

## Workflow
1. Confirm the user's target YAML files and intended deployment environment.
2. Read [rule reference](references/REFERENCE.md) and [primary documentation](references/SOURCES.md).
3. From the skill root run `python scripts/audit.py <path> --json` (install requirements first).
4. Inspect findings with rule IDs and filenames. Exit codes: 0 no findings, 1 findings, 2 invalid inputs/tool error.
5. Check ambiguous findings manually against the production context, versions, and owner intent. Do not silently apply changes.
6. Suggest specific safe improvements, discuss tradeoffs, and re-run on edited manifests.

## Demo
```bash
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yaml --json
python scripts/audit.py examples/review.yaml --json
python -m unittest discover -s tests -v
```

No network, credentials, kubectl, GitHub API, or execution of inspected YAML is required.
