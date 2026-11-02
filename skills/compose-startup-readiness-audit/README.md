<div align="center">
  <img src="assets/area-zero-logo-full.svg" alt="AREA ZERO original logo" width="210" />
  <h1>Compose Startup Readiness Audit</h1>
  <p><strong>Spot startup-order assumptions before they become first-run failures.</strong></p>
  <p>Offline, read-only Docker Compose review · Claude Code + Codex Agent Skill · Python 3.10+</p>
</div>

## Why this exists
Docker Compose starts dependencies before dependents but a started container isn't necessarily a ready application. This static auditor surfaces missing dependency services, readiness gates without healthchecks, dependency cycles and suspicious completion/restart combinations. It does **not** contact Docker or execute commands from input.

## Quickstart
```bash
python -m pip install 'PyYAML>=6,<7'
python scripts/audit.py examples/safe.yaml --strict
python scripts/audit.py examples/review.yaml --format json
python -m unittest discover -s tests -v
```

`--strict` exits **1** on error-severity findings, **0** otherwise; parse/input errors exit **2**. Plain mode reports review findings without failing. All output is deterministic and based on local synthetic fixtures.

## Agent installation
For **Claude Code**, copy this repository's folder into `.claude/skills/compose-startup-readiness-audit/` in your project or your user's Claude skills directory, preserving `SKILL.md`, `scripts/` and `references/`. For **Codex**, copy it into `.agents/skills/compose-startup-readiness-audit/` (or your agent's configured skills directory). Ask the agent: “Review my Compose startup readiness with this skill; don't deploy anything.”

## Example output
`python scripts/audit.py examples/review.yaml --strict` includes `DEPENDENCY_CYCLE`, `MISSING_HEALTHCHECK`, `MISSING_SERVICE`, and `STARTED_NOT_READY`. `examples/safe.yaml` reports `0 finding(s)`.

## What it detects
| Code | Meaning |
|---|---|
| `STARTED_NOT_READY` | Startup-order-only dependency; no readiness gate |
| `MISSING_HEALTHCHECK` | `service_healthy` target lacks an enabled check in inspected config |
| `DEPENDENCY_CYCLE` | Local dependency graph contains a cycle |
| `MISSING_SERVICE` | Referenced dependency service is not present |
| `CONFLICTING_RESTART` | Completion-based dependency has continuous restart policy |
| `OPTIONAL_DEPENDENCY` | Optional dependency may be unavailable |

See [`references/rules.md`](references/rules.md) for limitations and sources. Actual config interpolation, profiles, images' baked-in healthchecks, services from merged files and runtime readiness are **not** modeled; treat findings as starting points for review.

## Architecture, validation and security
One `yaml.safe_load_all` parse → bounded local service graph → deterministic findings. No Docker daemon, network request, shell invocation or dependency installs by input. Input size capped at 2MB. Tests use synthetic fixtures only. CI tests Python 3.10 and 3.12. No claim of a formal security audit or external review.

## Contributing / License / attribution
Open issues and PRs with a minimal synthetic fixture, expected code and relevant Compose specification. MIT License. Original AREA ZERO logo is owned by its creator and included unchanged for project attribution; the MIT code license does not relicense the logo. Docker and Compose trademarks are their owners'. Source: [Docker Compose services documentation](https://docs.docker.com/reference/compose-file/services/).
