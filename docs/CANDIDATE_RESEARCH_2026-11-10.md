# AREAZERO Skill Lab — EP.17 | Eight developer problems, two independent releases

**Date:** 2026-11-10 (Asia/Bangkok). **GitHub: RELEASED** after separate PR/main CI on Python 3.10 and 3.12. **Instagram @areazero.ai: OFF; Facebook AreaZero: OFF.** No social scheduling, Metricool writes, social GitHub workflow changes, or Daily AI Scout changes.

## Candidate scoring (internal editorial estimates, not third-party validation)

Criteria: usefulness /25, distinctiveness vs the prior 32 public skills /20, relevance to Claude Code/Codex /15, feasibility /15, developer audience /10, testability /10, clarity /5. Two highest-scoring candidates surpassed the >=85 release gate after scope was narrowed and reproducible tests were built; previously broad unsolved versions were rated lower. Scores are subjective and should not be presented as security performance metrics.

| Developer problem | Use /25 | Distinct /20 | Agent /15 | Feasible /15 | Audience /10 | Tests /10 | Clarity /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Cross-workflow case-insensitive GitHub Actions concurrency groups can overlap between workflow/job scopes and cancel release work | 24 | 17 | 15 | 14 | 9 | 9 | 5 | **93** | **RELEASED**; literal-only groups, no expression evaluation |
| Dockerfile secret-like ARG/ENV, optional secret mounts and credential-looking COPY paths can hide build-secret boundary mistakes | 24 | 15 | 15 | 14 | 9 | 9 | 5 | **91** | **RELEASED**; read-only Dockerfile static heuristics, not duplicate of dockerignore/context guard |
| GitHub deployment environment reviews are assumed enforced even when protection is configured elsewhere | 22 | 14 | 13 | 11 | 8 | 9 | 4 | 81 | HOLD; live environment settings must be separately checked |
| Kubernetes CronJob time zone, missed scheduling and DST expectations may diverge from rollout assumptions | 22 | 15 | 13 | 10 | 8 | 9 | 4 | 81 | HOLD; runtime controller time and DST scenarios need testing |
| Argo CD Replace/Force/Prune settings can be destructive in particular cluster versions | 22 | 14 | 13 | 10 | 8 | 8 | 4 | 79 | HOLD; cluster-specific controller state is not modeled |
| OpenTelemetry HTTP stable semantic-convention migration breaks downstream dashboards | 21 | 14 | 13 | 10 | 8 | 8 | 4 | 78 | HOLD; SDK- and configuration-specific |
| npm registry package provenance and signatures misread as an intrinsic package integrity guarantee | 21 | 13 | 13 | 10 | 8 | 8 | 4 | 77 | HOLD; trusted registry roots and online verification required |
| Terraform resource moves and removal blocks surprise teams during state refactors | 20 | 12 | 12 | 10 | 8 | 9 | 3 | 74 | HOLD; near existing Terraform Plan Impact Audit and deployment-specific |

## Official references reviewed

- GitHub Actions concurrency and queue behavior: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- Docker BuildKit secrets: https://docs.docker.com/build/building/secrets/
- Docker's SecretsUsedInArgOrEnv lint: https://docs.docker.com/reference/build-checks/secrets-used-in-arg-or-env/
- GitHub deployment environments: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- Kubernetes CronJob scheduling/timeZone: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
- Argo CD sync options: https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/
- OpenTelemetry HTTP semantic migration: https://opentelemetry.io/docs/specs/semconv/non-normative/http-migration/
- npm provenance verification: https://docs.npmjs.com/viewing-package-provenance/
- Agent Skills format: https://agentskills.io/specification

## Source, provisioning, PRs and verified CI

1. Reviewed latest GitHub production playbook on Bot_new_areazero branch areazero-social-assets plus portfolio operations, README and EPISODES. Owner's 2026-10-25 instruction disabling ALL Skill Lab social writes overrides historical playbook examples.
2. Staged **complete** packages on two nondefault agent-skills refs: `skill-lab/ep17-2026-11-10-concurrency` and `skill-lab/ep17-2026-11-10-buildkit`; no released source directory was added to portfolio main. Original official AREAZERO logo SVG was copied byte-for-byte from the previous independently published Skill.
3. Appended two new idempotent provisioning entries while preserving the original six: [Bot_new_areazero PR #4](https://github.com/Kanompung1988/Bot_new_areazero/pull/4), merged SHA `433a27e7fe9a99b6e5430a686ed54c4253e1716a`. [Authorized provisioning CI](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/42746578946) **SUCCESS**. Independently verified both target repositories owner Kanompung1988, visibility PUBLIC, default branch main.
4. [gha-concurrency-scope-audit](https://github.com/Kanompung1988/gha-concurrency-scope-audit): [merged PR #1](https://github.com/Kanompung1988/gha-concurrency-scope-audit/pull/1), PR head `fadc65f2a5224a1751b019d97c2106e4c6db003f`; [PR CI](https://github.com/Kanompung1988/gha-concurrency-scope-audit/actions/runs/42746957329) **SUCCESS** on Python 3.10 and 3.12. Public main SHA `9a80ff554212581c514c612ceb275145bf88acfc`; [post-merge main CI](https://github.com/Kanompung1988/gha-concurrency-scope-audit/actions/runs/42747180233) **SUCCESS**. Logs report **25 Python unittest cases** per matrix job, safe/review fixture smoke and frontmatter file checks passed.
5. [buildkit-secret-boundary-audit](https://github.com/Kanompung1988/buildkit-secret-boundary-audit): [merged PR #1](https://github.com/Kanompung1988/buildkit-secret-boundary-audit/pull/1), PR head `64ecb56be8c17f8e72eb55b9094c248a159b3d07`; [PR CI](https://github.com/Kanompung1988/buildkit-secret-boundary-audit/actions/runs/42747057147) **SUCCESS** on Python 3.10 and 3.12. Public main SHA `355aa00af4b2c09dfc9668e0ffaedafd4e74cab8`; [post-merge main CI](https://github.com/Kanompung1988/buildkit-secret-boundary-audit/actions/runs/42747186319) **SUCCESS**. Logs report **26 Python unittest cases** per matrix job, safe/review fixture smoke and frontmatter file checks passed.
6. Explicitly read back SKILL.md, README.md and CI from both public main branches after merge. Both tools are narrowly scoped offline static checks; their output does not prove runtime safety. **Official skills-ref validator NOT_RUN; third-party independent security review NOT_RUN.**

## Distribution and preservation

**GitHub: RELEASED / PUBLIC.** Instagram @areazero.ai: **OFF**. Facebook AreaZero: **OFF**. No Skill Lab social post was created, scheduled, rescheduled, updated for publication or published. Existing social draft and idempotency records unchanged. Daily AI Scout unchanged.
