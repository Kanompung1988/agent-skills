# AREAZERO Skill Lab — EP.23 developer research and independently verified releases

**Research/release date:** 2026-11-16 (Asia/Bangkok).
**GitHub code:** PUBLISHED in separate public repositories. **Skill Lab Social:** OFF indefinitely for Instagram @areazero.ai and Facebook Page AreaZero. No social write, schedule or reactivation. Daily AI Scout unchanged.

## Eight developer pain points and scoring

Editor-assigned 100-point scale: usefulness /25, distinctiveness /20, Claude/Codex relevance /15, feasible bounded implementation /15, audience /10, reproducible demonstration /10, communication /5. Scores are subjective internal judgments, **not external adoption, accuracy or formal security audit results**. Only a completed independent repository with real green CI and score >=85 may be called a release.

| Developer problem | Utility /25 | Distinct /20 | Agent /15 | Feasible /15 | Audience /10 | Demo /10 | Share /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Kubernetes topology spread selector/self-match, matchLabelKeys and minDomains review | 24 | 18 | 14 | 14 | 9 | 9 | 4 | **92** | **RELEASE** — bounded checks, 24 unit tests on 2 Python versions |
| Helm Chart.yaml/Chart.lock identity, missing lock and exact version contracts | 23 | 18 | 14 | 13 | 9 | 9 | 4 | **90** | **RELEASE** — deterministic local diff, 20 unit tests on 2 Python versions |
| Python PEP 660 editable vs wheel metadata/import parity | 21 | 16 | 13 | 13 | 8 | 8 | 3 | 82 | DEFER; must build/install real wheels and isolate backends |
| Kubernetes VolumeSnapshotClass deletion policy / restore input contracts | 21 | 15 | 12 | 13 | 8 | 8 | 3 | 80 | DEFER; CSI and controller realities not represented |
| Sigstore cosign signing identity and bundle boundary | 20 | 14 | 12 | 12 | 8 | 8 | 3 | 77 | DEFER; needs real cryptographic verification, overlapping prior attestation audit |
| Renovate scheduled lockfile maintenance / PR conflict detection | 19 | 14 | 12 | 12 | 8 | 8 | 3 | 76 | DEFER; manager rules and schedule evaluation too broad |
| Gateway API status observedGeneration freshness | 19 | 14 | 12 | 12 | 8 | 7 | 3 | 75 | DEFER; status depends on live controller, adjacent to ReferenceGrant audit |
| GitHub Actions self-hosted runner groups/labels compatibility | 19 | 12 | 13 | 12 | 8 | 8 | 3 | 75 | DEFER; current runner inventory/permissions needed, adjacent to existing GHA audits |

**Why the first two clear the gate now:** Both are explicitly narrowed to explainable contracts that can be reproduced from synthetic inputs, rather than claiming to emulate the complete Kubernetes scheduler or Helm. They fill new gaps in the 44-skill baseline; Kubernetes scheduling constraints are separate from the existing HPA/PDB audits, and chart *dependency lock drift* differs from Helm Values defaults. Higher scores than earlier deferred research reflect tighter scope and tested implementation, not proof of industry demand.

## Primary official technical references

1. Kubernetes topology spread API semantics (minDomains, nodeTaintsPolicy, matchLabelKeys): https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
2. Kubernetes selector semantics: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
3. Helm dependency build using Chart.lock: https://helm.sh/docs/helm/helm_dependency_build/
4. Helm Chart.yaml dependency format: https://helm.sh/docs/topics/charts/
5. PEP 660 editable wheels: https://peps.python.org/pep-0660/
6. Kubernetes volume snapshots and deletion behavior: https://kubernetes.io/docs/concepts/storage/volume-snapshots/
7. Sigstore cosign identity-verification guidance: https://docs.sigstore.dev/quickstart/quickstart-cosign/
8. Renovate lockfile maintenance documentation: https://docs.renovatebot.com/configuration-options/#lockfilemaintenance
9. Gateway API conditions reference: https://gateway-api.sigs.k8s.io/reference/spec/
10. GitHub self-hosted runner group/label routing: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
11. Agent Skills specification: https://agentskills.io/specification

## Release A — Kubernetes Topology Spread Audit (92/100)

- **Public independent repository:** https://github.com/Kanompung1988/k8s-topology-spread-audit
- **Staging (non-default branch):** `agent-skills/skill-lab/ep23-2026-11-16-topology-helm` under `skills/k8s-topology-spread-audit/`; staged implementation is **not** on portfolio main.
- **Release PR:** https://github.com/Kanompung1988/k8s-topology-spread-audit/pull/1 — MERGED.
- **Initial PR CI failed:** https://github.com/Kanompung1988/k8s-topology-spread-audit/actions/runs/43790044741 — invalid unquoted colon in SKILL.md YAML description; unit tests and both CLI fixtures had passed, frontmatter check failed. Fixed correctly on feature branch, updated staging source.
- **Corrected PR head:** `69675a079ca1b41c041e3b3320e955a733aff8ee`; [PR CI passed Python 3.10/3.12](https://github.com/Kanompung1988/k8s-topology-spread-audit/actions/runs/43790211305).
- **Verified public main commit:** `5b206fc63de6dc491c254220181f9281ceddbeda`.
- **Post-merge main CI:** https://github.com/Kanompung1988/k8s-topology-spread-audit/actions/runs/43790282199 — SUCCESS on Python 3.10 and 3.12. **24/24 tests per Python version** plus clean/review CLI and frontmatter/brand integrity checks.
- Scope: read-only rendered workload YAML (Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet, Job, CronJob). Excludes actual node eligibility, admission mutation, feature gates and kube-scheduler simulation. Not a production availability guarantee.

## Release B — Helm Dependency Lock Audit (90/100)

- **Public independent repository:** https://github.com/Kanompung1988/helm-dependency-lock-audit
- **Staging source:** same non-default `agent-skills` staging branch, under `skills/helm-dependency-lock-audit/`.
- **Release PR:** https://github.com/Kanompung1988/helm-dependency-lock-audit/pull/1 — MERGED.
- **PR head:** `2d00b8a753f892ee4d475f07fb43c2d0a16497ed`; [PR CI passed Python 3.10/3.12](https://github.com/Kanompung1988/helm-dependency-lock-audit/actions/runs/43790143136).
- **Verified public main commit:** `03276847b5c818eb15af0cbdabb5f1d812b95f90`.
- **Post-merge main CI:** https://github.com/Kanompung1988/helm-dependency-lock-audit/actions/runs/43790287883 — SUCCESS on Python 3.10 and 3.12. **20/20 tests per Python version** plus clean/review CLI and frontmatter/brand integrity checks.
- Scope: local Chart.yaml and Chart.lock identity/version review only. No semantic version constraint solving, no Helm library execution, no chart download or cryptographic provenance verification.

## Provisioning, verification and honesty gates

- Authorized idempotent repository request manifest [PR #10](https://github.com/Kanompung1988/Bot_new_areazero/pull/10) MERGED, with all 18 existing requests preserved and two new additions (20 total).
- [Provisioning workflow #43789814738](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/43789814738) — SUCCESS, created the two exact public repositories.
- Both target repositories have independently verified `PUBLIC` visibility and default branch `main`; root `SKILL.md` and `README.md` read from public `main` after release.
- Independent CI checks included real Python 3.10/3.12 workflow jobs, unit tests, safe/review fixtures, frontmatter smoke, unchanged Area Zero logo SHA256 and original SVG hero parsing.
- **Official `skills-ref` validator NOT_RUN.** No external code/security review. Passing CI is not comprehensive production certification.
- **Instagram/Facebook Skill Lab: OFF** — did not create, schedule, publish, reactivate or modify social drafts. **Daily AI Scout unchanged.**
