# AREAZERO Skill Lab — EP.22 candidate research & verified independent releases

**Date:** 2026-11-15 (Asia/Bangkok). **Skill Lab social OFF indefinitely.** Daily AI Scout not changed.

## Method and editorial score

Eight concrete developer issues were checked against official technical sources and the existing 42-skill portfolio. Score dimensions: **usefulness /25, distinctiveness /20, Claude/Codex relevance /15, feasible bounded implementation /15, audience /10, reproducible demonstration /10, explanation/shareability /5**. Only scores **>=85/100** accompanied by real passing GitHub Actions tests qualify as releases. These scores are subjective internal editorial judgments, not adoption measurements, formal security assessments, or proof of correctness in every cluster.

| Candidate pain point | Utility /25 | Distinct /20 | Agent /15 | Feasible /15 | Audience /10 | Demo /10 | Share /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Gateway API cross-namespace backend/certificate ReferenceGrant mismatches | 24 | 19 | 15 | 14 | 9 | 9 | 4 | **94** | **RELEASE**: exact from/to/namespace matching, TLS and mirror support |
| Argo Rollouts AnalysisTemplate threshold and Rollout reference drift | 23 | 19 | 14 | 14 | 9 | 9 | 4 | **92** | **RELEASE**: metric gates and local template/arg references |
| Python PEP 660 editable vs regular wheel parity | 21 | 16 | 13 | 13 | 8 | 8 | 3 | 82 | Defer; real backend builds/isolated environments needed, avoid duplicate Python packaging tools |
| Kubernetes topologySpreadConstraints selector/minDomains edge cases | 21 | 15 | 12 | 13 | 8 | 8 | 3 | 80 | Defer; requires scheduling/version-specific simulations |
| Helm Chart.lock vs Chart.yaml dependency drift | 20 | 15 | 12 | 13 | 8 | 8 | 3 | 79 | Defer; needs chart dependency resolver parity and differentiation from Helm Values skill |
| Sigstore/cosign verification identity vs artifact boundary | 20 | 14 | 11 | 13 | 8 | 8 | 3 | 77 | Defer; verification must use cryptography, overlaps attestation gate review |
| Dependabot-triggered secret scope misunderstandings | 19 | 12 | 13 | 13 | 8 | 8 | 3 | 76 | Defer; overlaps GHA trust and reusable workflow permissions audits |
| Renovate lockfile maintenance schedule/PR conflicts | 18 | 13 | 11 | 12 | 8 | 8 | 3 | 73 | Defer; schedule and manager/version behavior needs stronger demonstrations |

## Official primary references used

1. Gateway API ReferenceGrant API and cross-namespace trust: https://gateway-api.sigs.k8s.io/reference/api-types/referencegrant/
2. Gateway API TLS cross-namespace Secret references: https://gateway-api.sigs.k8s.io/guides/user-guides/tls/
3. Argo Rollouts analysis and threshold behavior: https://argo-rollouts.readthedocs.io/en/latest/features/analysis/
4. Argo Rollouts zero-count and step/background behavior: https://argoproj.github.io/argo-rollouts/features/analysis/
5. PEP 660 editable wheel behavior: https://peps.python.org/pep-0660/
6. Kubernetes topology-spread constraints: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
7. Helm dependency build and Chart.lock: https://helm.sh/docs/helm/helm_dependency_build/
8. Sigstore signature verification: https://docs.sigstore.dev/cosign/verifying/verify/
9. Dependabot GitHub Actions constraints: https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions
10. Renovate lockfile maintenance options: https://docs.renovatebot.com/configuration-options/#lockfilemaintenance
11. Agent Skills format: https://agentskills.io/specification

## Release A — Gateway API ReferenceGrant Audit (94/100)

- **Public standalone repository:** https://github.com/Kanompung1988/gateway-referencegrant-audit
- **Staging source:** `agent-skills` non-default branch `skill-lab/ep22-2026-11-15-gateway`; never copied to portfolio main.
- **PR #1:** https://github.com/Kanompung1988/gateway-referencegrant-audit/pull/1 — **MERGED**.
- **PR CI (Python 3.10 + 3.12):** https://github.com/Kanompung1988/gateway-referencegrant-audit/actions/runs/43666045811 — SUCCESS.
- **Merged public main commit:** `fd8be8eaf928d0d2eb909b8bb999a900d39403a9`.
- **Post-merge main CI (Python 3.10 + 3.12):** https://github.com/Kanompung1988/gateway-referencegrant-audit/actions/runs/43666573492 — SUCCESS.
- **Actual test count per version:** **26/26** from workflow job logs. Separate safe/review CLI fixtures and frontmatter checks PASS.
- Scope: offline static inspection only, not an effective cluster Gateway policy proof. Special mesh Route exceptions are not certified.

## Release B — Argo Rollouts Analysis Audit (92/100)

- **Public standalone repository:** https://github.com/Kanompung1988/argo-rollouts-analysis-audit
- **Staging source:** `agent-skills` non-default branch `skill-lab/ep22-2026-11-15-rollouts`.
- **PR #1:** https://github.com/Kanompung1988/argo-rollouts-analysis-audit/pull/1 — **MERGED**.
- **PR CI (Python 3.10 + 3.12):** https://github.com/Kanompung1988/argo-rollouts-analysis-audit/actions/runs/43666072646 — SUCCESS.
- **Merged public main commit:** `cf8a77103c9fabb76ccc542da50f3476e3ed4519`.
- **Post-merge main CI (Python 3.10 + 3.12):** https://github.com/Kanompung1988/argo-rollouts-analysis-audit/actions/runs/43666578616 — SUCCESS.
- **Actual test count per version:** **35/35** from workflow job logs. Separate safe/review CLI fixtures and frontmatter checks PASS.
- **Honest correction before release:** Initial staging code incorrectly flagged `count: 0` as invalid. Official Argo Rollouts documentation confirms zero is valid with distinct background vs step behavior. Corrected analyzer, tests, fixture and README on the staging branch *before* opening the standalone PR; the green CI tested the corrected version.
- Scope: no CEL evaluation, metric-provider execution or real AnalysisRun simulation.

## Repository provisioning and honesty gates

- Authorized manifest PR: https://github.com/Kanompung1988/Bot_new_areazero/pull/9 — MERGED. Preserved existing 16 requests and added only these two, total 18.
- Repo provisioning Action: https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/43665874996 — SUCCESS.
- Both exact target repos independently verified PUBLIC with `main` default; `SKILL.md` and README fetched from public main after release.
- Both PR and post-merge CI verified green for Python 3.10/3.12; no claims about actual production traffic or security.
- Official `skills-ref` validator: **NOT_RUN**. Independent third-party audit: **NOT_DONE**. The GitHub Actions frontmatter smoke tests are not substitutes for official validation.
- **SOCIAL: OFF** (Instagram @areazero.ai / Facebook AreaZero). No Metricool/social write, schedule, reactivation or changes to old drafts. Daily AI Scout untouched.

## Final post-release quality enhancement (PR #2 in each standalone repository)

Both repositories subsequently received **original SVG hero artwork**, a contributor guide, and a real CI check that the supplied official Area Zero logo matches the known source SHA256 `89b459e6a4e61748d2d56d54da2cd17ff2b55deafbbc90e45e43d4c319462d16` and that both SVG assets parse as XML. These are public code/docs changes, not marketing/social publication.

- Gateway enhancement [PR #2](https://github.com/Kanompung1988/gateway-referencegrant-audit/pull/2) **MERGED**. Final public main `fd8be8eaf928d0d2eb909b8bb999a900d39403a9`; [post-merge CI SUCCESS](https://github.com/Kanompung1988/gateway-referencegrant-audit/actions/runs/43666573492), Python 3.10/3.12 both passed unit, fixture, frontmatter, original logo SHA256 and hero parse checks.
- Argo Rollouts enhancement [PR #2](https://github.com/Kanompung1988/argo-rollouts-analysis-audit/pull/2) **MERGED**. Final public main `cf8a77103c9fabb76ccc542da50f3476e3ed4519`; [post-merge CI SUCCESS](https://github.com/Kanompung1988/argo-rollouts-analysis-audit/actions/runs/43666578616), Python 3.10/3.12 both passed unit, fixture, frontmatter, original logo SHA256 and hero parse checks.

No production cluster/controller integration or independent audit was performed. Official `skills-ref` validation remains **NOT_RUN**. Skill Lab social remains OFF, Daily AI Scout unchanged.
