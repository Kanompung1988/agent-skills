# AREAZERO Skill Lab — EP.15 | Eight screened developer failure modes and verified GitHub release

**Date:** Sunday 2026-11-08 (Asia/Bangkok). **Code: RELEASED** (two independent PUBLIC repositories). **Instagram @areazero.ai: OFF / Facebook AreaZero: OFF** under owner override of 2026-10-25. No social write/scheduling/workflow activation. Daily AI Scout was not modified.

## Scoring: eight concrete, nonidentical developer pain points

Weights: usefulness **25**, distinctiveness versus existing 28 skills **20**, Claude Code/Codex relevance **15**, feasibility **15**, developer audience **10**, reproducible testability **10**, clarity **5**. Scores are internal editorial judgments, not third-party endorsements, independent adoption or security certification.

| Candidate failure mode | Utility/25 | Distinct/20 | Agent/15 | Feasible/15 | Audience/10 | Tests/10 | Clarity/5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GitHub Actions attestation gate: producers omit OIDC/attestation permissions or consumers suppress a failed verify command, leaving downloaded builds without a meaningful provenance gate | 24 | 18 | 15 | 14 | 9 | 9 | 4 | **93** | **RELEASED**: static workflow contract, not actual signature verification |
| Kubernetes ValidatingAdmissionPolicy Binding: a policy has no supplied binding, binding only Warn/Audit, references unresolved policy/paramRef or allows missing parameters | 23 | 18 | 15 | 14 | 9 | 9 | 4 | **92** | **RELEASED**: version-bounded offline manifest relationship review |
| Docker BuildKit secret mounts and ARG/ENV leaks: build tokens persist or escape into metadata; overlapping existing docker-context-guard | 22 | 11 | 14 | 12 | 9 | 9 | 4 | 81 | HOLD; substantial overlap and unknown runtime flow |
| GitHub deployment environment protection: an environment is not gated as owner expected; environment settings are remote and not established by workflow YAML | 21 | 13 | 13 | 11 | 8 | 9 | 4 | 79 | HOLD; effective settings require GitHub API permission |
| npm registry signature / provenance: hash integrity confused with publisher identity, verification depends on remote registry and trust roots | 22 | 11 | 13 | 10 | 8 | 8 | 4 | 76 | HOLD; unavailable offline trust evidence |
| OpenTelemetry HTTP semconv migration: mixed old/stable attributes break dashboards and metric units during rollout | 21 | 12 | 13 | 11 | 8 | 9 | 3 | 77 | HOLD; instrumented versions and runtime settings vary |
| Argo CD sync-option interactions: prune, replace and server-side apply change ownership or deployment drift | 21 | 12 | 13 | 10 | 8 | 8 | 4 | 76 | HOLD; cluster/controller behavior cannot be safely modeled from fragments |
| Helm schema and overrides: values.schema.json may reject values when flags/parent chart override defaults | 20 | 11 | 12 | 10 | 8 | 8 | 3 | 72 | HOLD; existing Helm values contract tool and templating context |

**Why EP15 candidates crossed the threshold despite backlog holds:** Attestation was narrowed to a GitHub workflow *configuration and fail-open gate* review (not signature cryptography). VAP was narrowed to explicit v1 policy/binding relationships and parameter actions (not CEL evaluation or live resource selection). Tests cover actionable synthetic safe and failure scenarios. This improves feasibility and separation from earlier skills; it does not prove novelty across the entire ecosystem.

## Primary source references

1. GitHub action behavior, permissions and signing: https://github.com/actions/attest ; https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
2. Why verification needs identity, owner and trusted roots: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline
3. Reusable workflow signer scoping: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/increase-security-rating
4. Kubernetes VAP, bindings, parameterNotFoundAction and failurePolicy: https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
5. Kubernetes v1 policy/binding schema: https://kubernetes.io/docs/reference/kubernetes-api/admissionregistration/validating-admission-policy-v1/ ; https://kubernetes.io/docs/reference/kubernetes-api/admissionregistration/validating-admission-policy-binding-v1/
6. Docker BuildKit secrets vs ARG/ENV: https://docs.docker.com/build/building/secrets/
7. GitHub deployment environment gates: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
8. npm package signature/provenance references: https://docs.npmjs.com/cli/v11/commands/npm-audit/
9. OpenTelemetry HTTP migration: https://opentelemetry.io/docs/specs/semconv/non-normative/http-migration/
10. Argo CD sync options: https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/
11. Helm values schema / overrides: https://helm.sh/docs/topics/charts/
12. Canonical Agent Skills spec: https://agentskills.io/specification

## Build, provisioning, CI and public release evidence

- Read latest Bot_new_areazero playbook from branch areazero-social-assets, portfolio operations/README/episode catalog, and official Agent Skills specification. **Only production/development instructions were used; older social sections were not treated as authorization.**
- Built **exactly two** independent skill packages: each has root spec SKILL.md, README with Claude Code/Codex installation, MIT LICENSE, unchanged original AREAZERO SVG, read-only PyYAML CLI, synthetic safe/review fixtures, unit tests, authoritative references and separate .github/workflows/ci.yml.
- Staged **22 files total** on nondefault portfolio branch skill-lab/ep15-2026-11-08-attestation-vap at commit fe040564e94a61def214ffb5bb3ffc4ec9405571. These files are **not present on portfolio main**, avoiding duplicate skill source.
- Extended existing provisioning manifest **without removing EP14 requests**, via Bot_new_areazero [PR #2](https://github.com/Kanompung1988/Bot_new_areazero/pull/2), merged commit aeccf0c76566004514d0666eab21dd53ffe19836. Authorized [provisioning run #42437210255](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/42437210255) completed SUCCESS. Public identity/main checked separately.

**1. [gha-attestation-gate-audit](https://github.com/Kanompung1988/gha-attestation-gate-audit)**

- [Merged implementation PR #1](https://github.com/Kanompung1988/gha-attestation-gate-audit/pull/1); latest PR head d7614e518091c819f2f5191a46476cd1f460d1df; [PR CI SUCCESS](https://github.com/Kanompung1988/gha-attestation-gate-audit/actions/runs/42437336974).
- Public main after merge commit **313e1a166d2fdadb1cea904d3d021e042249c905**; [main CI SUCCESS](https://github.com/Kanompung1988/gha-attestation-gate-audit/actions/runs/42437469431).
- **22/22 unit tests per Python version** (3.10 and 3.12), safe/review CLI JSON fixture exit checks, frontmatter shape smoke; job conclusions and log checked. Scanner never invokes actual GitHub CLI or verifies a signing certificate.

**2. [k8s-vap-binding-audit](https://github.com/Kanompung1988/k8s-vap-binding-audit)**

- [Merged implementation PR #1](https://github.com/Kanompung1988/k8s-vap-binding-audit/pull/1); latest PR head eb6a0508b5927418a2e82bc0a7beabbcbc9f7e73; [PR CI SUCCESS](https://github.com/Kanompung1988/k8s-vap-binding-audit/actions/runs/42437417373).
- Public main after merge commit **5d876735667231de64f32be4aa31febd392194dd**; [main CI SUCCESS](https://github.com/Kanompung1988/k8s-vap-binding-audit/actions/runs/42437474848).
- **25/25 unit tests per Python version** (3.10 and 3.12), safe/review CLI fixture smoke, frontmatter shape smoke. Local v1 YAML only; not a CEL interpreter, live cluster policy or admission API acceptance test.

All public default-branch SKILL.md and README were read back separately and validated against exact public repo identity; logo blob SHA e1d2a0686010b251a530f9ad7eaf9afddf6a706b unchanged. Both repositories preserve branch/PR review evidence. **Official skills-ref validator: NOT_RUN**. No external audit or real-production dataset is claimed. All tool limitations and heuristics are documented in references.

## Release vs. social status

**GitHub CODE: PUBLISHED** in two new public independent repositories with successful PR/main CI. **Instagram: OFF. Facebook: OFF.** No scheduled, restored, changed-to-autoPublish or published Skill Lab social items; no Metricool call. Historical social drafts unchanged. **Daily AI Scout unchanged**, including its own publishing workflow. The portfolio is an index only.