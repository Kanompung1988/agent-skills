# AREAZERO Skill Lab — EP.27 Candidate Research and Verified Release Evidence

**Date:** 2026-11-20 (Asia/Bangkok) · **Portfolio:** [agent-skills](https://github.com/Kanompung1988/agent-skills) · **Skill Lab social OFF indefinitely** by owner instruction. Daily AI Scout not changed.

## Eight concrete developer pain points

Editorial score rubric: usefulness (25), originality versus existing 52 skills (20), Claude Code/Codex suitability (15), feasibility (15), audience (10), demonstrability/tests (10), shareability (5). Scores are internal estimates, not measured user demand. >=85 alone does not authorize release without tests, PR checks and public default-branch verification.

| Developer problem | Use | Unique | Agent | Feasible | Audience | Test | Share | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Docker Compose profiles excluding required dependent services | 24 | 19 | 14 | 14 | 9 | 9 | 4 | **93** | RELEASED after real tests |
| Kubernetes Pod Security Admission Namespace labels/policy mistakes | 24 | 19 | 14 | 14 | 9 | 8 | 4 | **92** | RELEASED after real tests |
| Renovate lockfile maintenance schedule and regeneration conflicts | 21 | 17 | 13 | 12 | 9 | 7 | 3 | **82** | No release; scheduler and package-manager semantics need more proof |
| GitHub self-hosted runner groups and labels stranding queued jobs | 21 | 16 | 12 | 12 | 9 | 7 | 3 | **80** | No release; live runner inventory, ARC and org permissions vary |
| Sigstore keyless signer identity and OIDC issuer mismatch | 21 | 17 | 11 | 10 | 9 | 8 | 3 | **79** | No release; cannot substitute heuristics for cryptographic verification |
| Gateway API observedGeneration and controller status freshness | 20 | 17 | 12 | 11 | 8 | 7 | 3 | **78** | No release; effective status depends on controller timing |
| Helm OCI provenance and chart authenticity | 20 | 15 | 11 | 12 | 8 | 8 | 3 | **77** | No release; trust/provenance overlap |
| PostgreSQL default privileges and role/grant migration drift | 20 | 13 | 12 | 11 | 8 | 7 | 4 | **75** | No release; effective role/default-grant evaluation requires database state |

**Duplicate check:** Existing [Compose Startup Readiness Audit](https://github.com/Kanompung1988/compose-startup-readiness-audit) checks depends_on/health readiness. EP.27 Compose focuses on profile **selection** and whether declared dependencies are activated in modeled scenarios. Existing [Kubernetes SecurityContext Audit](https://github.com/Kanompung1988/k8s-securitycontext-audit) checks workload-level settings, while EP.27 PSA checks Namespace policy **label contracts**, not individual Pod Security Standards compliance.

## Standalone release 1 — Docker Compose Profile Dependency Audit (93/100)

- Public repository: https://github.com/Kanompung1988/compose-profile-dependency-audit
- [Release PR #1](https://github.com/Kanompung1988/compose-profile-dependency-audit/pull/1) merged; public default-branch `main` SHA `684611cd7ba01294b61196d915d0ee074b1e5a5d`.
- [PR CI](https://github.com/Kanompung1988/compose-profile-dependency-audit/actions/runs/44659324224) SUCCESS and [post-merge main CI](https://github.com/Kanompung1988/compose-profile-dependency-audit/actions/runs/44659440171) SUCCESS; 32 unit tests and safe/review CLI fixture execution **per Python 3.10/3.12** job; SVG and Agent Skills metadata QA checks.
- Local Python 3.13: 32/32 unit tests pass. The tool only models one local Compose file; profiles and target scenario outcomes are review leads, not actual deployment status.
- Sources: [official Compose profiles specification](https://docs.docker.com/reference/compose-file/profiles/) and [profile invocation guidance](https://docs.docker.com/compose/how-tos/profiles/).

## Standalone release 2 — Kubernetes Pod Security Admission Namespace Audit (92/100)

- Public repository: https://github.com/Kanompung1988/k8s-psa-namespace-audit
- [Release PR #1](https://github.com/Kanompung1988/k8s-psa-namespace-audit/pull/1) merged; public default-branch `main` SHA `f3dea55f34b40d2eeb58382ed32928cb4b00b411`.
- [PR CI](https://github.com/Kanompung1988/k8s-psa-namespace-audit/actions/runs/44659379779) SUCCESS and [post-merge main CI](https://github.com/Kanompung1988/k8s-psa-namespace-audit/actions/runs/44659474154) SUCCESS; 36 unit tests and safe/review CLI fixture execution **per Python 3.10/3.12** job; SVG and Agent Skills metadata QA checks.
- Local Python 3.13: 36/36 tests pass. Cannot infer real cluster defaults, admission controller availability, exemptions or Pod compliance. Minimum enforcement is a **user policy input**.
- Sources: [Kubernetes Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/), [namespace enforcement](https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/), [official label reference](https://kubernetes.io/docs/reference/labels-annotations-taints/).

## Provisioning, packaging and evidence boundaries

- Authorized [Bot_new_areazero PR #16](https://github.com/Kanompung1988/Bot_new_areazero/pull/16) merged; [Provisioning workflow](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/44659197671) SUCCESS. Preserved 27 prior idempotent request records and added only two new requests (**29 total**).
- Complete source packages staged under `skills/<slug>/` on non-default branch `agent-skills:skill-lab/ep27-2026-11-20-profiles-psa`. The portfolio `main` is index-only; individual repositories contain their actual source and CI.
- Each repository includes root `SKILL.md`, Python CLI, README, synthetic safe/review YAML fixtures, tests, original logo (checksum-guarded), original branded hero SVG, MIT code license, Claude Code/Codex installation instructions, reference material and contributing/security guidelines.
- Metadata/frontmatter validation passed independent CI. Official `skills-ref validate`: **NOT_RUN** (not installed in local environment). No external security review or production system guarantee.
- **GitHub code releases: PUBLISHED** only after PR/main CI and public default-branch checks. **Skill Lab Instagram/Facebook: OFF / DRAFT ONLY**; no Metricool or social workflow writes, no scheduling, no publishing. Daily AI Scout untouched.