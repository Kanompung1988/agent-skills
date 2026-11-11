<p align="center"><img src="assets/areazero-logo.svg" width="200" alt="AREAZERO original logo"></p>

# Kubernetes CronJob Timezone & Schedule Audit

**An offline, explainable Agent Skill for configuration review.** Review Kubernetes CronJob YAML for time zones, daylight-saving shifts, short starting deadlines, concurrency replacement and missed-run hazards. Use before deploying batch schedules.

## Install
```bash
git clone https://github.com/Kanompung1988/k8s-cronjob-timezone-audit.git
cd k8s-cronjob-timezone-audit
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yaml --json
python scripts/audit.py examples/review.yaml --json
python -m unittest discover -s tests -v
```

**Claude Code:** `git clone https://github.com/Kanompung1988/k8s-cronjob-timezone-audit.git .claude/skills/k8s-cronjob-timezone-audit`

**Codex:** `git clone https://github.com/Kanompung1988/k8s-cronjob-timezone-audit.git .agents/skills/k8s-cronjob-timezone-audit`

From the installed skill root run `python scripts/audit.py PATH --json`. The agent should follow [SKILL.md](SKILL.md), explain each finding, and never edit user data without permission.

## Safety and scope
Static YAML review only. Does not contact clusters or perform deployment. Checks are intentionally conservative, bounded to the documented fields, and cannot prove actual production safety. Exit codes: 0 clean; 1 findings; 2 invalid configuration or parser/IO errors. Tool ignores symlinks and files larger than 2 MiB. Review [rules](references/REFERENCE.md), [primary docs](references/SOURCES.md), and fixtures before relying on results.

MIT-licensed source and tests. AREAZERO logo remains a separate brand asset, not granted under the software MIT license.
