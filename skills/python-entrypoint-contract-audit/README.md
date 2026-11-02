<div align="center">
  <img src="assets/area-zero-logo-full.svg" alt="Original AREA ZERO logo" width="210" />
  <h1>Python Entry-point Contract Audit</h1>
  <p><strong>Find broken console-script metadata before your CLI disappears from the install.</strong></p>
  <p>Zero execution of package code · Claude Code + Codex Agent Skill · Python 3.10+</p>
</div>

## Why
Python packaging's entry-point metadata is easy to misconfigure. This read-only linter finds malformed object references, reserved group conflicts, duplicate command names, dynamic/static conflicts, and suspicious local module targets **without importing code or running a build backend**.

## Quickstart
```bash
# Python 3.10 only: python -m pip install 'tomli>=2'
python scripts/audit.py examples/safe.toml --no-target-check --strict
python scripts/audit.py examples/review.toml --no-target-check --format json
python scripts/audit.py ./pyproject.toml --strict
python -m unittest discover -s tests -v
```

CLI exit codes: 0 = clean or review-only findings, 1 = `error` findings with `--strict`, 2 = unreadable/malformed TOML. `--no-target-check` omits local module-existence heuristics.

## Install as an Agent Skill
For **Claude Code**, copy the entire repository into `.claude/skills/python-entrypoint-contract-audit/`; for **Codex**, copy it to `.agents/skills/python-entrypoint-contract-audit/`. Keep `SKILL.md`, `scripts/`, and `references/` together. Prompt example: “Audit our CLI entry point definitions before publishing; do not install or execute project code.”

## What gets checked
`[project.scripts]`, `[project.gui-scripts]`, reserved `[project.entry-points.console_scripts]` / `.gui_scripts`, syntax and names, duplicated commands, dynamic/static overlap and optional local module file existence in the root or `src/`. Example malformed fixtures produce `INVALID_REFERENCE`, `DUPLICATE_COMMAND`, and `PRIVATE_TARGET` review signals.

## Architecture / safety
A size-bounded TOML parse (builtin `tomllib` or `tomli` on Python 3.10), conservative reference grammar, and optional local file checks. No import, subprocess, network request, wheel building, or code execution from the inspected repository. Does not check callable presence, actual import resolution, namespace package resolution, or generated build outputs. Target-file findings are **review-only** because custom backends and dynamic metadata exist.

## Verification / Contributing / attribution
CI on Python 3.10 and 3.12 runs unit tests and safe/broken synthetic fixtures. Report reproductions with a minimal `pyproject.toml` and expected finding code. This code is MIT licensed. AREA ZERO logo is included in original form for attribution; trademarks and third-party assets are not relicensed under MIT. References: [PyPA pyproject specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) and [entry points](https://packaging.python.org/en/latest/specifications/entry-points/).
