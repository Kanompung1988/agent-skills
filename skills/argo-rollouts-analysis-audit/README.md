<p align="center"><img src="assets/areazero-logo.svg" alt="Original Area Zero brand logo" width="270"></p>

# Argo Rollouts Analysis Audit

**Review metric gates and template contracts before a canary or blue-green rollout.**

[![Independent CI](https://github.com/Kanompung1988/argo-rollouts-analysis-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/argo-rollouts-analysis-audit/actions/workflows/ci.yml) · MIT · Python 3.10+

## Problem

Progressive delivery can pause on an Inconclusive AnalysisRun, unexpectedly fail an analysis or reference a missing AnalysisTemplate. Subtle settings such as `failureLimit: -1` combined with `consecutiveSuccessLimit: 0` need specific review. The analyzer takes a directory of **rendered local YAML**, checks bounded metric semantics and reference relationships, and explains each finding without running the rollout.

## Quick start

```bash
git clone https://github.com/Kanompung1988/argo-rollouts-analysis-audit.git
cd argo-rollouts-analysis-audit
python -m pip install 'PyYAML>=6,<7'
python scripts/audit.py examples/safe.yaml --json     # clean, exit 0
python scripts/audit.py examples/review.yaml --json   # findings, exit 1
python scripts/audit.py ./rendered-manifests --json
python -m unittest discover -s tests -v
```

JSON fields: `count`, `findings` (`code`, `severity`, `file`, `resource`, `message`, `remediation`). Exit 0 = no finding in input, 1 = review finding, 2 = invalid input.

## Install in Claude Code or Codex

- **Claude Code**: `git clone https://github.com/Kanompung1988/argo-rollouts-analysis-audit.git ~/.claude/skills/argo-rollouts-analysis-audit`
- **Codex**: `git clone https://github.com/Kanompung1988/argo-rollouts-analysis-audit.git ~/.agents/skills/argo-rollouts-analysis-audit`

Place the entire repo at the destination to keep `SKILL.md` and `scripts/` together. Reload skill discovery. Format: https://agentskills.io/specification.

## What it does / does not do

Supports `argoproj.io/v1alpha1` AnalysisTemplates and ClusterAnalysisTemplates with per-metric condition, provider, limit and count checks (including valid count=0, whose semantics depend on analysis placement); Rollout inline/background canary and blue-green template references; namespace vs cluster-scoped matching; missing required arguments.

Limitations: Does not evaluate CEL, verify measurement queries/provider credentials, predict actual traffic behavior, inspect live resources, or know installed controller version. Some warnings are **intentional manual-approval policies**, not bugs. Incomplete bundles create scope warnings. Analyzer reads only local YAML with safe parser and file size/count limits. CI runs real tests and fixture smoke on Python 3.10/3.12; official `skills-ref` validation: **NOT_RUN**, unless separately recorded.

[Rule reference](references/REFERENCE.md) · [Primary docs](references/SOURCES.md) · [MIT LICENSE](LICENSE). Area Zero name/logo remain protected brand assets outside the MIT software grant.
