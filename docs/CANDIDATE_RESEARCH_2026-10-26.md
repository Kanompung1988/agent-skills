# AREAZERO Skill Lab — candidate selection, 2026-10-26

Internal editorial scoring, not independent validation. Weighting: usefulness 25, originality/distinctiveness 20, Claude Code/Codex relevance 15, feasibility 15, audience 10, reproducible demos/tests 10, presentability 5. An idea scoring at least 85 can be built only if its real checks pass. Some proposed names/features overlap existing third-party tools: novelty scores measure specificity/usefulness, not claims of invention.

| Candidate developer pain point | Utility | Distinct | Agent fit | Feasible | Audience | Tests | Demo | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GitHub Actions privilege and PR trust boundaries are easy to misconfigure | 24 | 18 | 15 | 14 | 9 | 10 | 5 | **95** | Build `gha-trust-boundary-audit`; focus on line-based evidence and benign explanations |
| `.env.example` drifts from Python/Node/Vite variable usage at deploy | 23 | 17 | 15 | 15 | 10 | 10 | 5 | **95** | Build `env-contract-audit`, names-only never inspect live `.env` |
| MCP tool-output prompt injection can redirect coding agents | 24 | 16 | 14 | 9 | 10 | 7 | 4 | 84 | Defer; safe evaluations and policy model require careful treatment |
| Terraform secret output/state accidentally exposes sensitive values | 23 | 16 | 13 | 9 | 8 | 7 | 3 | 79 | Defer: avoid producing a misleading security scanner |
| Artifact attestation/provenance can be hard to verify across CI stages | 21 | 14 | 13 | 11 | 9 | 8 | 4 | 80 | Defer: GitHub CLI supports attestation verify already; avoid duplication |
| Missing deployment health checks / unstable endpoint drift | 21 | 14 | 13 | 11 | 9 | 9 | 4 | 81 | Defer; requires platform-specific contracts |
| OpenAPI breaking changes during SDK release | 24 | 10 | 14 | 15 | 10 | 10 | 4 | 87 | **Reject duplicate**: already published as `openapi-compat-audit` EP.01 |
| Noisy CI logs obscure the failing stage | 23 | 9 | 14 | 15 | 10 | 10 | 4 | 85 | **Reject duplicate**: already published as `ci-log-triage` EP.01 |

## Evidence and source URLs (checked 2026-10-26)
- GitHub Actions privileged `pull_request_target`, unsafe fork checkout: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- Shell-injection risk from untrusted PR/event values: https://docs.github.com/en/actions/concepts/security/script-injections
- Workflow-level `GITHUB_TOKEN` permission principle: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Vite client exposure of `VITE_` variables: https://vite.dev/guide/env-and-mode
- Artifact provenance/verification: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- OWASP agentic attacks through untrusted repo text/PR comments: https://genai.owasp.org/2026/07/08/genai-and-agentic-ai-exploit-roundup-q2-2026/
- Existing EP.01 releases: https://github.com/Kanompung1988/agent-skills/blob/main/docs/EPISODES.md
- Open Agent Skills spec: https://agentskills.io/specification

Scope: static analysis only; no claim of a formal security audit or independent review. Running unit tests locally and on GitHub CI does not prove absence of false positives or vulnerabilities. Skills have separate README, SKILL.md, scripts, tests, examples, and license; brand SVG excluded from MIT code license.