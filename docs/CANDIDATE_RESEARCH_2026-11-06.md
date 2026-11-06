# AREAZERO Skill Lab — EP.13 research and release evidence
**Date:** Friday, 2026-11-06 (Asia/Bangkok). **GitHub code: RELEASED. Skill Lab social: OFF** by owner override dated 2026-10-25. No Metricool or social-write action occurred in EP.13. Daily AI Scout unchanged.

## Eight distinct developer pain points, editorial scoring

Scoring weights: usefulness / developer utility **25**, originality and nonduplication **20**, agent suitability **15**, engineering feasibility **15**, audience **10**, reproducibility/demonstration **10**, communication **5**, total **100**. Scores are internal editorial assessments—not market adoption or independent review.

| Candidate and real developer failure mode | Utility /25 | Originality /20 | Agent /15 | Feasibility /15 | Audience /10 | Testability /10 | Clarity /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Docker Compose host bind mounts: a supposedly read-only service still writes to host paths or exposes `docker.sock` | 24 | 18 | 15 | 15 | 9 | 10 | 4 | **95** | **Released**; distinct from existing Compose startup and port audits |
| GitHub reusable workflow caller: external mutable `jobs.uses`, `secrets: inherit`, excessive inherited token scope | 24 | 18 | 15 | 14 | 9 | 9 | 4 | **93** | **Released**; different scope than existing GHA Trust Boundary audit |
| Kubernetes container securityContext: inherited runAsNonRoot/capabilities/seccomp interactions | 22 | 14 | 14 | 14 | 9 | 8 | 3 | 84 | Hold; cross-pod admission context not modeled |
| GitHub artifact attestations: missing provenance verification at release consuming boundary | 21 | 15 | 13 | 12 | 8 | 9 | 3 | 81 | Hold; verification needs real signatures/claims |
| Git submodule provenance: branch tracking and unaudited commit pointer changes | 21 | 13 | 13 | 13 | 9 | 8 | 3 | 80 | Hold; risk of shallow static false positives |
| GitHub deployment environment protection: required reviewer/restrictions hard to distinguish from config file alone | 21 | 12 | 12 | 13 | 9 | 8 | 3 | 78 | Hold; effective settings API required |
| Helm values override contracts: schema/template drift across layered overrides | 20 | 12 | 14 | 11 | 8 | 9 | 3 | 77 | Hold; significant overlap with existing Helm Values Contract Audit |
| OpenTelemetry semantic conventions migration: old/new HTTP attribute overlap and rollout toggle | 20 | 11 | 13 | 11 | 8 | 9 | 3 | 75 | Hold; requires version-aware instrumentation support |

## Primary sources / proof of underlying pain

- Docker bind mounts are write-enabled unless set readonly, and `ro` changes mount filesystem access: https://docs.docker.com/engine/storage/bind-mounts/
- Docker Compose services volume configuration: https://docs.docker.com/reference/compose-file/services/
- GitHub reusable workflow calls, secrets, token scoping, immutable refs: https://docs.github.com/en/actions/how-tos/sharing-automations/reusing-workflows and https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations
- Kubernetes Pod Security Standards / securityContext: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- GitHub artifact attestations: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
- Git submodules reference: https://git-scm.com/docs/gitsubmodules
- GitHub deployment environment protection: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- Helm chart schemas: https://helm.sh/docs/topics/charts/
- OpenTelemetry stable HTTP semantic convention migration: https://opentelemetry.io/docs/specs/semconv/non-normative/http-migration/

## Verified, independent public GitHub release evidence

**Creation/provisioner:** portfolio staging nondefault branch `skill-lab/ep13-2026-11-06-mount-reusable` at commit `8d4d1c6ff39c43506af4d6234b7fbc3e7ca2ebf0`; authorized manifest on Bot_new_areazero main commit `d9497feef18d06e4ac115b487b810376e643704e`; [public repository provisioning Actions run — SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/42150095072). No skill source committed to portfolio main.

**Skill 1: [compose-mount-write-audit](https://github.com/Kanompung1988/compose-mount-write-audit)** — [PR #1 merged](https://github.com/Kanompung1988/compose-mount-write-audit/pull/1). PR head `d6b8c36db38b6bea501af7c97b1973e541469b4d`, merged public main commit `67c8f30a8245972f799dd715d737a1abb0ee6612`. [PR CI SUCCESS](https://github.com/Kanompung1988/compose-mount-write-audit/actions/runs/42150198805); [post-merge main CI SUCCESS](https://github.com/Kanompung1988/compose-mount-write-audit/actions/runs/42150375137). Python 3.10 + 3.12: **20/20 unit tests per version**, safe CLI exit 0 and flagged CLI exit 1, frontmatter spec-smoke. Source uses offline PyYAML; no Docker or network. Public README, SKILL.md, MIT license, original preserved SVG, examples, source and CI checked after merge.

**Skill 2: [gha-reusable-permission-audit](https://github.com/Kanompung1988/gha-reusable-permission-audit)** — [PR #1 merged](https://github.com/Kanompung1988/gha-reusable-permission-audit/pull/1). PR head `ed2292552289e640931d3ab6b9f133fa94f80d0c`, merged public main commit `cc3974a44cb8470500e733e81fea13def232672f`. [PR CI SUCCESS](https://github.com/Kanompung1988/gha-reusable-permission-audit/actions/runs/42150274284); [post-merge main CI SUCCESS](https://github.com/Kanompung1988/gha-reusable-permission-audit/actions/runs/42150383349). Python 3.10 + 3.12: **19/19 unit tests per version**, safe CLI exit 0 and review CLI exit 1, frontmatter spec-smoke. No GitHub API calls by analyzer or secret value disclosure. Public README, SKILL.md, MIT license, SVG, examples, source and CI checked after merge.

Both CI job matrices (3.10, 3.12) completed SUCCESS, independently confirmed from GitHub Actions jobs. Python test counts come from actual CI job logs, not a synthetic estimated tally.

**Official `skills-ref` validator:** **NOT_RUN**. Both repos did run a local frontmatter/spec-shape smoke, not an official conformance certification. No independent third-party review, no real production runtime validation, no guarantee of all security vulnerabilities found. Contents of public repositories can be installed for Claude Code / Codex as documented.

## Social distribution — explicit no-write status

**Instagram @areazero.ai: OFF**. **Facebook AreaZero: OFF**. No Skill Lab posts drafted for automatic publication, scheduled, updated or published in this run. GitHub code releases and social distribution are independent. Daily AI Scout remains unchanged.
