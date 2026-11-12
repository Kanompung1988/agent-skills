<p align="center"><img src="assets/area-zero-logo-full.svg" alt="AREAZERO logo" width="220"></p>

# GitHub Actions Environment Gate Audit

[![Python CI](https://github.com/Kanompung1988/gha-environment-gate-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/gha-environment-gate-audit/actions/workflows/ci.yml)

A portable [Agent Skill](https://agentskills.io/specification) for **Claude Code** and **OpenAI Codex**. Audit GitHub Actions workflow deployment jobs against an explicitly supplied GitHub environment-settings inventory. Use for PR reviews of deployment gates, required reviewers, branch restrictions and environment bindings before releases.

**Read-only, local static analysis. No network, cloud credentials, shell commands from analyzed files, or production mutations.**

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yml --inventory examples/inventory.json --json
python scripts/audit.py examples/review.yml --inventory examples/inventory.json --json  # exits 1 when findings are present
python -m unittest discover -s tests -v
```

Use a **reviewed** environment inventory (never infer the settings from YAML):

```bash
python scripts/audit.py .github/workflows --inventory examples/inventory.json --json
```

The sample `inventory.json` is illustrative and can be stale. GitHub's Settings → Environments is the authoritative configuration. Without an inventory, the auditor emits `ENV004` rather than claiming a gate is protected.


## Install in an agent

Clone this repository and copy its entire directory (including `SKILL.md`, `scripts/`, `references/` and dependencies) into your agent's local skills directory. Claude Code users can place the folder under `.claude/skills/gha-environment-gate-audit/` within a project or their user skills directory. Codex users can place it under `.agents/skills/gha-environment-gate-audit/` in a project or user skills directory, according to their installed client version. Restart/rescan skills if required. Do not copy only `SKILL.md`: the local script and references are part of the skill.

## Output and exit status

JSON output has `files_scanned` and `findings` (each has a stable rule ID and location). Exit status `0` means no *supported* findings, not a security certification; `1` findings; `2` invalid input. Rule explanations: [reference](references/REFERENCE.md). Primary documentation: [sources](references/SOURCES.md).

## Security and scope

GitHub environments and their settings are not stored in workflow YAML. The optional inventory is a manually reviewed snapshot, never live verification; jobs with vague names can evade deployment detection. Do not infer production protection without checking the GitHub repository settings.

No input is executed. Scan only files you are authorized to inspect. CI tests synthetic fixtures on Python 3.10/3.12 and checks basic frontmatter. The official `skills-ref` validator and third-party review are **not claimed** unless independently run and recorded.

## Contribute

Open Issues with a minimal reproducible, non-sensitive fixture. PRs should add tests for every behavior change and preserve read-only guarantees. MIT software license; original AREAZERO trademark/logo is excluded from the software license.
