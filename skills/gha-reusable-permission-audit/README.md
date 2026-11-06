<p align="center"><img src="assets/areazero-logo.svg" alt="Original AREAZERO logo" width="360"></p>

# GitHub Actions Reusable Permission Audit

**Reusable CI workflows simplify maintenance, but blur the boundary between a caller's token, inherited secrets, and externally sourced code.** Offline Agent Skill for Claude Code and Codex that reviews GitHub Actions *caller* workflows before merging.

[![CI](https://github.com/Kanompung1988/gha-reusable-permission-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/gha-reusable-permission-audit/actions/workflows/ci.yml)

## Installation

```bash
git clone https://github.com/Kanompung1988/gha-reusable-permission-audit.git
cd gha-reusable-permission-audit
python -m pip install -r requirements.txt
```

For Claude Code clone to `.claude/skills/gha-reusable-permission-audit`, for Codex to `.agents/skills/gha-reusable-permission-audit` and consult [Agent Skills specification](https://agentskills.io/specification).

## CLI / tests

```bash
python scripts/audit.py examples/safe.yml --json     # exit 0
python scripts/audit.py examples/review.yml --json   # exit 1
python scripts/audit.py .github/workflows/your.yml --json
python -m unittest discover -s tests -v
```

Checks `jobs.<id>.uses` local/external scope, full SHA pinning, `secrets: inherit` on external calls, write tokens and `pull_request_target` combinations. Findings only include generic job/rule messages, never secret names or mapping values. Python 3.10/3.12 CI required.

**Limitations:** single-file static heuristic; doesn't fetch called workflow, nested reusable calls, fork context, effective organization/repository permissions, event privileges, or ensure security. Local workflows may legitimately use `secrets: inherit`. See [rule details](references/RULES.md), external official docs [Reusable workflows](https://docs.github.com/en/actions/how-tos/sharing-automations/reusing-workflows) and [Token permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication). MIT software [LICENSE](LICENSE); original logo excluded by [BRAND.md](BRAND.md).
