<p align="center"><img src="assets/area-zero-logo-full.svg" alt="AREAZERO logo" width="220"></p>

# Terraform State Transition Audit

[![Python CI](https://github.com/Kanompung1988/terraform-state-transition-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/terraform-state-transition-audit/actions/workflows/ci.yml)

A portable [Agent Skill](https://agentskills.io/specification) for **Claude Code** and **OpenAI Codex**. Review Terraform moved and removed HCL blocks for conflicting moves, cycles, duplicated targets and state handoffs missing destroy=false. Use when reviewing Terraform refactors or resource retirement pull requests before terraform plan and apply.

**Read-only, local static analysis. No network, cloud credentials, shell commands from analyzed files, or production mutations.**

## Quick start

```bash
python --version
python scripts/audit.py examples/safe.tf --json
python scripts/audit.py examples/review.tf --json  # exits 1 when findings are present
python -m unittest discover -s tests -v
```

Run a read-only scan of a Terraform directory:

```bash
python scripts/audit.py infrastructure/ --json
```

This cannot interpret evaluated Terraform state or a real plan; treat static declarations as review hints.


## Install in an agent

Clone this repository and copy its entire directory (including `SKILL.md`, `scripts/`, `references/` and dependencies) into your agent's local skills directory. Claude Code users can place the folder under `.claude/skills/terraform-state-transition-audit/` within a project or their user skills directory. Codex users can place it under `.agents/skills/terraform-state-transition-audit/` in a project or user skills directory, according to their installed client version. Restart/rescan skills if required. Do not copy only `SKILL.md`: the local script and references are part of the skill.

## Output and exit status

JSON output has `files_scanned` and `findings` (each has a stable rule ID and location). Exit status `0` means no *supported* findings, not a security certification; `1` findings; `2` invalid input. Rule explanations: [reference](references/REFERENCE.md). Primary documentation: [sources](references/SOURCES.md).

## Security and scope

This lightweight lexical reviewer is not an HCL parser, Terraform plan, or state interpreter. It supports simple static resource/module addresses. Unknown/dynamic addresses are manual-review findings, not proven errors. Never apply Terraform solely on this audit; validate and review an actual plan against the target workspace.

No input is executed. Scan only files you are authorized to inspect. CI tests synthetic fixtures on Python 3.10/3.12 and checks basic frontmatter. The official `skills-ref` validator and third-party review are **not claimed** unless independently run and recorded.

## Contribute

Open Issues with a minimal reproducible, non-sensitive fixture. PRs should add tests for every behavior change and preserve read-only guarantees. MIT software license; original AREAZERO trademark/logo is excluded from the software license.
