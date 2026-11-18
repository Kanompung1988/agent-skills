<p align="center"><img src="assets/area-zero-logo-full.svg" alt="Original AREAZERO logo" width="230"></p>
<p align="center"><img src="assets/hero.svg" alt="gha-reusable-input-contract-audit hero" width="100%"></p>

# GitHub Actions Reusable Input Contract Audit

[![CI](https://github.com/Kanompung1988/gha-reusable-input-contract-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/gha-reusable-input-contract-audit/actions/workflows/ci.yml) [Agent Skills spec](https://agentskills.io/specification) · MIT

**Avoid mismatched workflow interfaces before a release pipeline runs.** Offline scan of local `workflow_call` callers for required inputs and secrets, undeclared names, and static boolean/number typing. It does *not* access secrets or inspect remote workflows.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe/.github/workflows --json
python scripts/audit.py examples/review/.github/workflows --json
python -m unittest discover -s tests -v
```

Exit 0 clean (or review-only with default threshold), 2 errors, 1 input failure. Use `--fail-on review` to gate all findings; `--fail-on never` for informational-only. JSON contains code, file, job, severity, and advice. All fixtures are synthetic.

## Claude Code and Codex

Clone this standalone repository and install it as an Agent Skill by placing its **whole contents** at `~/.claude/skills/gha-reusable-input-contract-audit/` for Claude Code, or `~/.agents/skills/gha-reusable-input-contract-audit/` for Codex. Preserve root `SKILL.md`, scripts, requirements, and references. Activate when reviewing local reusable workflow call sites, run the CLI against a checked-out project, and inspect the findings before changing CI.

## Guarantees and limits

Read-only YAML static analysis; no GitHub credentials, network calls, dynamic expression evaluation, or claims about live secrets. Only local `./.github/workflows/*.yml`/`.yaml` references are resolved. Tests cover synthetic failure modes. See [reference](references/REFERENCE.md), [contributing](CONTRIBUTING.md), and [MIT License](LICENSE). Independent security review is not claimed.
