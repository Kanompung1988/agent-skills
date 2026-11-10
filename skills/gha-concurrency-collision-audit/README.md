<p align="center"><img src="assets/areazero-logo.svg" alt="Original AREAZERO logo" width="240"></p>

# GitHub Actions Concurrency Collision Audit

A portable, read-only Agent Skill detecting workflow/job concurrency groups that might cancel unexpected GitHub Actions builds or releases.

## Install in Claude Code or Codex

Clone this standalone repository to `.claude/skills/gha-concurrency-collision-audit` (Claude Code) or `.agents/skills/gha-concurrency-collision-audit` (Codex). Review code before running it; match the directory to the SKILL.md `name`.

```sh
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yml --json
python scripts/audit.py examples/review.yml --json
python scripts/audit.py .github/workflows --json
python -m unittest discover -s tests -v
```

Exit 0 means no **static** finding, 1 means review, 2 invalid input. The scanner makes no network calls, does not run target workflow commands, and does not print secrets or input YAML contents.

## What it catches

Case-insensitive group equality across jobs/workflows; unsupported queue+cancel combination; missing head_ref fallback; overly broad group identity and potential cancellation of deployment workflows. Group collisions may be intentional. Dynamic expression values, run timing, matrix values, permission and protected environments are **not** evaluated. Synthetic tests only. Passing CI is not a security certification.

Read [rules](references/REFERENCE.md), [GitHub primary source](references/SOURCES.md), and [Agent Skills specification](https://agentskills.io/specification). MIT license.
