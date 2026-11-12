# AREAZERO Skill Lab — EP.19 research and independently verified release
Date: 2026-11-12 (Asia/Bangkok). Social distribution: **OFF** by owner instruction 2026-10-25; Daily AI Scout unchanged.

## Selection method
Eight concrete developer problems screened against the existing 36 public portfolio entries. Internal editorial weights: usefulness 25, distinctiveness 20, Claude/Codex relevance 15, feasibility 15, audience 10, demonstrability 10, shareability 5. Only candidates >=85 that pass actual tests are eligible for release. Scores are internal editorial assessments, not measured user demand or third-party endorsements.

| Candidate/problem | Use | Distinct | Agent | Feas | Audience | Demo | Share | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GitHub Actions environment approval/branch-gate drift | 25 | 19 | 15 | 15 | 10 | 9 | 1 | **94** | **SHIPPED** as gha-environment-gate-audit |
| Terraform moved/removed state handoff contracts | 25 | 18 | 15 | 15 | 9 | 9 | 1 | **92** | **SHIPPED** as terraform-state-transition-audit |
| Kubernetes StatefulSet PVC retention changes during scale-down/deletion | 22 | 16 | 13 | 13 | 8 | 8 | 1 | 81 | Hold: needs complete version-aware semantics |
| npm registry provenance and trusted publisher mismatch | 23 | 15 | 13 | 10 | 9 | 8 | 2 | 80 | Hold: cannot verify provenance offline without trusted registry evidence |
| OpenTelemetry HTTP semantic convention migration drift | 21 | 15 | 13 | 11 | 9 | 8 | 2 | 79 | Hold: specification and SDK version interactions need stronger fixtures |
| Docker build SBOM/provenance attestation consistency | 20 | 14 | 13 | 11 | 9 | 8 | 2 | 77 | Hold: overlapping existing BuildKit and attestation tools |
| Python editable-install and built-wheel import parity | 21 | 14 | 13 | 12 | 8 | 7 | 1 | 76 | Hold: environment-dependent and overlaps existing Python artifacts coverage |
| Dependabot-triggered workflow secret scopes | 20 | 11 | 13 | 13 | 9 | 8 | 1 | 75 | Hold: close overlap with existing GHA trust/permissions audits |

## Primary evidence and boundaries
- [GitHub deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments): environment-level approvals, branch rules, secrets, and plan restrictions. GitHub YAML does **not** encode effective repository settings, so a local manually reviewed inventory is optional and cannot prove a gate is configured.
- [GitHub manage environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments): protect environment, branch/tag settings and gate configuration.
- [Terraform moved blocks](https://developer.hashicorp.com/terraform/language/block/moved): from/to address mapping and non-destructive move semantics.
- [Terraform removed blocks](https://developer.hashicorp.com/terraform/language/block/removed) and [remove from state](https://developer.hashicorp.com/terraform/language/state/remove): lifecycle destroy=false prevents destruction when handing off management; explicit destroy=true may be intentional and requires review, not always an error.
- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/): PVC retention decisions.
- [npm trusted publishers](https://docs.npmjs.com/trusted-publishers/) and [npm provenance](https://docs.npmjs.com/generating-provenance-statements/): provenance depends on publisher and registry.
- [Dependabot Actions rules](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions): secret/token constraints.

## Verified independent releases (GitHub)
| Gate | GitHub Actions Environment Gate Audit | Terraform State Transition Audit |
|---|---|---|
| Repository | [gha-environment-gate-audit](https://github.com/Kanompung1988/gha-environment-gate-audit) | [terraform-state-transition-audit](https://github.com/Kanompung1988/terraform-state-transition-audit) |
| Release PR | [PR #1 merged](https://github.com/Kanompung1988/gha-environment-gate-audit/pull/1) | [PR #1 merged](https://github.com/Kanompung1988/terraform-state-transition-audit/pull/1) |
| Brand hero PR | [PR #2 merged](https://github.com/Kanompung1988/gha-environment-gate-audit/pull/2) | [PR #2 merged](https://github.com/Kanompung1988/terraform-state-transition-audit/pull/2) |
| Public default-branch SHA | `fd6e063e3008ee670b0c3e236821968601fc2c43` | `12eddfff7c5494e3e6fc1f1e443516cb5d6a1190` |
| Final main CI | [CI run 43141649976](https://github.com/Kanompung1988/gha-environment-gate-audit/actions/runs/43141649976) | [CI run 43141655483](https://github.com/Kanompung1988/terraform-state-transition-audit/actions/runs/43141655483) |
| Unit tests (per Python version) | 29/29 | 37/37 |
| CLI demos / frontmatter | Safe/review + basic frontmatter smoke pass | Safe/review + basic frontmatter smoke pass |

Provisioning: [Bot_new_areazero PR #6](https://github.com/Kanompung1988/Bot_new_areazero/pull/6) merged; [authorized provisioning run #43141120049](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/43141120049) succeeded. Both public standalone repositories contain their own SKILL.md, scripts, tests, documentation, examples, source links, MIT code license, immutable original Area Zero logo assets, hero SVG and CI. No source was merged into the portfolio default branch.

**Failure-and-fix trace:** The first Terraform PR CI run ([43141265660](https://github.com/Kanompung1988/terraform-state-transition-audit/actions/runs/43141265660)) failed because the metadata smoke test imported PyYAML that was not installed. All 37 tests passed, but CI correctly failed; a separate requirements fix on the same PR installed PyYAML for CI validation only. The next PR CI and both post-merge CI runs passed. No success was claimed before the correction.

**Limits and honesty:** GitHub environment inventory is manual, not an authenticated API check. Terraform analyzer is lexical, not a full HCL parser, plan reader or backend verifier. Both are read-only. Official `skills-ref` validator **NOT_RUN**, independent reviewer **NOT_DONE**, real production system validation **NOT_DONE**. Scores are internal. No Skill Lab Instagram/Facebook post was created, scheduled or updated; Daily AI Scout was not changed.
