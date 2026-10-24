# Areazero Open Source Lab — candidate evaluation

**Date:** 2026-10-24 (Asia/Bangkok). Brainstormed eight specific developer problems, reviewed public documentation, chose two whose scripts could be built/tested in a single local session. Scores are **editorial estimates, not externally measured demand**.

Scoring weights: utility (25), distinctiveness (20), agent/dev relevance (15), build feasibility (15), potential audience (10), demo/evidence (10), social content (5).

| Rank | Problem / skill concept | Utility | Distinct | Agent/dev | Feasible | Audience | Demo | Social | Total | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | OpenAPI contract drift detection | 24 | 19 | 14 | 14 | 9 | 9 | 5 | **94** | **Build** `openapi-compat-audit` |
| 2 | CI log evidence/root-cause triage | 23 | 16 | 15 | 15 | 8 | 10 | 5 | **92** | **Build** `ci-log-triage` |
| 3 | PR change-to-test mapping | 23 | 13 | 14 | 12 | 8 | 8 | 5 | 83 | Hold; requires live repository awareness |
| 4 | Flaky test pattern investigator | 21 | 15 | 13 | 11 | 8 | 9 | 5 | 82 | Hold; repeated-run evidence needed |
| 5 | Environment-variable contract drift | 20 | 17 | 13 | 11 | 7 | 8 | 4 | 80 | Hold; manifests vary widely |
| 6 | Dependency upgrade regression detector | 23 | 13 | 14 | 9 | 8 | 8 | 4 | 79 | Hold; higher ecosystem complexity |
| 7 | Docs-to-test evidence matrix | 20 | 14 | 13 | 12 | 7 | 8 | 4 | 78 | Hold; limited distinctiveness |
| 8 | Release rollback preflight | 22 | 11 | 12 | 7 | 7 | 8 | 4 | 71 | Hold; would need deployment-specific integrations |

## Source basis checked in this run

- Official Agent Skills specification (directory, frontmatter, progressive disclosure, validation): https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
- GitHub Actions log retrieval / search / diagnosis (demonstrates actual investigation workflow): https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs
- GitHub troubleshooting workflow guidance (why hypotheses should be tied to logs and reproducible tests): https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
- GitHub Agentic Workflows debugging guide (further examples of evidence-first triage): https://github.github.com/gh-aw/troubleshooting/debugging/

A marketplace survey of all existing Agent Skills **was not completed**; original-work claims are limited to scripts authored in this run, not a claim of unique concept. At first research time the target repository returned 404. This was a historical blocker; use the current public `main` branch as the publication source of truth.
