# AREAZERO Skill Lab — EP.21 candidate research and verified releases

**Date:** 2026-11-14, Asia/Bangkok. **Skill Lab social publishing: OFF indefinitely.** Daily AI Scout untouched.

## Evaluation method

Eight practical developer problems were researched against primary technical documents and screened against the previous 40 standalone portfolio skills to avoid near-duplicates. Subjective editorial score: usefulness /25, originality or distinctiveness from existing work /20, Claude Code/Codex relevance /15, feasible and bounded implementation /15, audience /10, reproducible demonstration /10, sharing clarity /5. **Only >=85/100 and real green independent CI** may be counted as a release. These are internal scores, not measured adoption or third-party security audit results.

| Candidate developer pain point | Utility /25 | Distinct /20 | Agent /15 | Feasible /15 | Audience /10 | Demo /10 | Share /5 | Total /100 | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| npm trusted publisher identity and OIDC workflow setup drift | 24 | 19 | 15 | 14 | 9 | 9 | 4 | **94** | **SHIP** — bounded offline package and publish workflow audit |
| OpenTelemetry HTTP stable semantic-convention migration drift | 23 | 19 | 14 | 14 | 9 | 9 | 4 | **92** | **SHIP** — sanitized OTLP JSON analysis |
| Python PEP 660 editable installation vs built-wheel parity | 21 | 16 | 13 | 13 | 8 | 8 | 3 | 82 | Defer — backend-dependent behavior, avoid inaccurate guarantees |
| Gateway API cross-namespace backend ReferenceGrant gaps | 21 | 15 | 13 | 12 | 8 | 8 | 4 | 81 | Defer — broaden test coverage for exceptions and versioning |
| Argo Rollouts AnalysisTemplate error/threshold configuration | 20 | 15 | 13 | 12 | 8 | 8 | 3 | 79 | Defer — need production-realistic validation cases |
| Docker BuildKit SBOM/provenance output preservation | 21 | 13 | 12 | 11 | 9 | 8 | 3 | 77 | Defer — partly overlaps earlier attestation tooling |
| Dependabot-triggered workflow secret/permission scope | 19 | 11 | 13 | 12 | 8 | 8 | 3 | 74 | Reject for now — overlap with existing GitHub Actions trust skills |
| Helm OCI chart provenance and digest reference drift | 19 | 11 | 12 | 11 | 8 | 8 | 4 | 73 | Defer — overlap and incomplete safe verification model |

## Primary documentation

1. npm Trusted Publishing: https://docs.npmjs.com/trusted-publishers/ — OIDC publishing requirements, public-repository provenance conditions and trusted-publisher configuration. Static inventory is not registry truth.
2. OpenTelemetry HTTP semconv: https://opentelemetry.io/docs/specs/semconv/http/http-spans/ and migration: https://opentelemetry.io/docs/specs/semconv/non-normative/http-migration/ — `http` and `http/dup` modes and old/new attributes.
3. Python editable installs: https://peps.python.org/pep-0660/
4. Gateway API ReferenceGrant: https://gateway-api.sigs.k8s.io/reference/spec/#referencegrant
5. Argo Rollouts analysis: https://argo-rollouts.readthedocs.io/en/stable/features/analysis/
6. Docker build attestations: https://docs.docker.com/build/metadata/attestations/ and https://docs.docker.com/build/metadata/attestations/sbom/
7. GitHub Dependabot Actions restrictions: https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions
8. Helm OCI registry: https://helm.sh/docs/topics/registries/
9. Agent Skills packaging specification: https://agentskills.io/specification

## EP.21 verification of two independent public code releases

| Gate | npm Trusted Publisher Audit | OTel HTTP Semconv Audit |
|---|---|---|
| Standalone public default branch | [`main` SKILL.md](https://github.com/Kanompung1988/npm-trusted-publisher-audit/blob/main/SKILL.md) | [`main` SKILL.md](https://github.com/Kanompung1988/otel-http-semconv-audit/blob/main/SKILL.md) |
| Standalone README and installation | [README](https://github.com/Kanompung1988/npm-trusted-publisher-audit/blob/main/README.md) | [README](https://github.com/Kanompung1988/otel-http-semconv-audit/blob/main/README.md) |
| PR review and merge | [PR #1 — merged](https://github.com/Kanompung1988/npm-trusted-publisher-audit/pull/1) | [PR #1 — merged](https://github.com/Kanompung1988/otel-http-semconv-audit/pull/1) |
| Post-merge default branch SHA | `5b7b8014e8a26ed51340b45c19fd062296380880` | `1eeb22497dea67169f261ff5cd9c9038d1a2cd3a` |
| Main CI results | [SUCCESS, Python 3.10/3.12, 20 tests + demo](https://github.com/Kanompung1988/npm-trusted-publisher-audit/actions/runs/43545264327) | [SUCCESS, Python 3.10/3.12, 24 tests + demo](https://github.com/Kanompung1988/otel-http-semconv-audit/actions/runs/43544891749) |
| Offline behavior | Local package and YAML review, no npm invocation | Sanitized JSON sample analysis, no telemetry backend |
| Agent Skill format | Frontmatter smoke tested in CI; official skills-ref **NOT_RUN** | Frontmatter smoke tested in CI; official skills-ref **NOT_RUN** |

**Provisioning:** [Automated GitHub repository provisioner — SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/43544525090); the request manifest preserved all preceding 14 cumulative idempotency entries and added exactly two new ones. The provisioner is not standalone skill CI.

**Security and scientific caveats:** The npm script recognizes direct publish commands in workflow YAML but cannot prove that the remote package is configured for trusted publishing, or assess all shell/third-party action paths. The OTel script examines at most 10,000 spans in a sanitized file, outputs no attribute values, and its route-cardinality signal is a heuristic; a sample cannot prove global production migration completeness. No independent external review. Neither releases marketing/social content.

## Social policy and release guard

- **GitHub code release:** Verified independently on public `main` and green CI as above.
- **Instagram @areazero.ai: OFF. Facebook AreaZero: OFF.** No Skill Lab schedule, publish, activation, modification, or Metricool write.
- **Daily AI Scout:** Its workflows and publishing schedule remain unchanged.
