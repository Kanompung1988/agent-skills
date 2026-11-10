<p align="center"><img src="assets/areazero-logo.svg" width="240" alt="Original AREAZERO logo"></p>

# Docker BuildKit Secret Boundary Audit

A small, offline, read-only Agent Skill for catching Dockerfile build-time credential handling pitfalls. Unlike build context checks, this focuses on credential persistence via Dockerfile ARG/ENV and per-RUN BuildKit secret mounts.

## Install for Claude Code / Codex

Clone this standalone repository into `.claude/skills/docker-build-secret-boundary-audit` (Claude Code) or `.agents/skills/docker-build-secret-boundary-audit` (Codex). Inspect source before running, and preserve SKILL.md folder name.

```sh
python scripts/audit.py examples/safe.Dockerfile --json
python scripts/audit.py examples/review.Dockerfile --json
python scripts/audit.py Dockerfile --json
python -m unittest discover -s tests -v
```

Exit 0 no detected static findings, 1 human review needed, 2 invalid input. Never prints values from Dockerfile or runs a build. No network, credentials, Docker daemon or extra Python dependencies.

## Boundaries

Detects heuristic secret-looking ARG/ENV names, optional secret mounts, missing same-RUN `/run/secrets/<id>` mount, and risky references to sensitive ARG/ENV names. It cannot prove actual leakage, parse every exotic Dockerfile syntax, resolve all variable expansion, or determine runtime application behavior. Docker has built-in `SecretsUsedInArgOrEnv` build check; use `docker build --check` independently. Passing tests does not imply production security.

See [rule reference](references/REFERENCE.md), [Docker official documentation](references/SOURCES.md), [Agent Skills specification](https://agentskills.io/specification) and MIT license.
