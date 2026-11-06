<p align="center"><img src="assets/areazero-logo.svg" width="360" alt="Original AREAZERO logo"></p>

# Compose Mount Write Audit

**Which host paths are still writable when a container is set read-only?** This reusable Agent Skill and offline CLI helps Claude Code and Codex review short/long Compose bind mounts, Docker socket exposure (`:ro` is not API protection), and uncertain paths. Independent tool, no daemon required.

[![CI](https://github.com/Kanompung1988/compose-mount-write-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/compose-mount-write-audit/actions/workflows/ci.yml)

## Install

```bash
git clone https://github.com/Kanompung1988/compose-mount-write-audit.git
cd compose-mount-write-audit
python -m pip install -r requirements.txt
```

For **Claude Code**, clone the repo into `.claude/skills/compose-mount-write-audit`. For **Codex**, clone it into `.agents/skills/compose-mount-write-audit`. Follow [Agent Skills specification](https://agentskills.io/specification) and client skill discovery settings.

## Run / test

```bash
python scripts/audit.py examples/safe.yml --json    # exit 0
python scripts/audit.py examples/review.yml --json  # exit 1
python scripts/audit.py compose.yaml --json
python -m unittest discover -s tests -v
```

**Exit:** 0 = no modeled findings, 1 = review, 2 = invalid input. Reports include service, container target, rule, severity; host source paths are not echoed. CI tests Python 3.10 and 3.12.

## Limitations and contributions

Analyzes **one** local Compose YAML document only. No runtime Docker inspection, merged `-f` overrides, interpolation, host symlink resolution, Windows drive normalization, named volume permissions, production safety guarantees. Suggest separately running `docker compose config` in an authorized environment. See [rule boundaries](references/RULES.md). Add regressions before changing behavior. MIT software [LICENSE](LICENSE), original logo excluded under [BRAND.md](BRAND.md).
