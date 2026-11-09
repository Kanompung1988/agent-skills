# AREAZERO Skill Lab — EP.16 | Eight developer pain points, two independently tested releases

**Date:** 2026-11-09 (Asia/Bangkok). **GitHub code: RELEASED** after individual successful PR/main CI. **Instagram @areazero.ai: OFF; Facebook AreaZero: OFF.** No social scheduling, autoPublish, Metricool write, marketing workflow edits, or change to Daily AI Scout.

## Candidate screening and editorial scoring

Weights: usefulness 25, distinctiveness vs 30 already-released skills 20, Claude Code/Codex relevance 15, implementation feasibility 15, audience 10, reproducible testability 10, clarity 5. These are subjective in-house editorial scores, not outside evaluation or popularity metrics.

| Concrete developer failure mode | Useful/25 | Distinct/20 | Agent/15 | Feasible/15 | Audience/10 | Tests/10 | Clear/5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HPA CPU/memory Utilization with missing workload container resource requests, plus sidecars, duplicate scaling targets, and target reference mismatch | 24 | 19 | 15 | 14 | 10 | 9 | 4 | **95** | **RELEASED**; static autoscaling/v2 cross-object review |
| Service selector doesn't match supplied same-namespace Pod templates; named targetPort missing on matching workload | 24 | 18 | 15 | 14 | 9 | 9 | 4 | **93** | **RELEASED**; bounded offline cross-object review |
| GitHub Actions concurrency group collisions and accidental cancellation across release jobs | 22 | 13 | 14 | 12 | 9 | 9 | 4 | 83 | HOLD; expressions and per-workflow run context cannot be reliably resolved from fragments |
| Docker BuildKit secret mount misuse versus persistent ARG/ENV | 22 | 11 | 14 | 12 | 9 | 9 | 4 | 81 | HOLD; overlaps Docker Context Guard; actual build metadata not verified |
| GitHub deployment environment protection differs from expectations in workflow YAML | 21 | 13 | 13 | 11 | 8 | 9 | 4 | 79 | HOLD; effective approval gates are remote settings, not established by manifest |
| npm package registry provenance confused with package integrity hashes | 21 | 11 | 13 | 10 | 8 | 9 | 4 | 76 | HOLD; signature verification needs trusted remote roots |
| OpenTelemetry HTTP semantic-convention migration breaks dashboards/units | 21 | 12 | 13 | 11 | 8 | 9 | 3 | 77 | HOLD; live SDK versions and switches vary |
| Argo CD prune/replace/server-side apply interactions may change resources unexpectedly | 21 | 12 | 13 | 10 | 8 | 8 | 4 | 76 | HOLD; controller/cluster state not modeled from local YAML |

**Narrow, defensible scopes:** HPA scanner only analyzes autoscaling/v2 resource utilization and supplied target workloads, not arbitrary custom/external metrics or live admission/defaults. Service scanner compares only selector/Pod-template declarations; selectorless and ExternalName Services are allowed; it cannot check actual ready endpoints.

## Official references reviewed

- Kubernetes HPA controller and request dependencies: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/
- Kubernetes Service selectors and selectorless Endpoints: https://kubernetes.io/docs/concepts/services-networking/service/
- GitHub Actions concurrency: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Docker BuildKit secrets: https://docs.docker.com/build/building/secrets/
- GitHub deployment environments: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- npm provenance: https://docs.npmjs.com/generating-provenance-statements
- OpenTelemetry HTTP semconv migration: https://opentelemetry.io/docs/specs/semconv/non-normative/http-migration/
- Argo CD sync options: https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/
- Agent Skills specification: https://agentskills.io/specification

## Build, stage, provision, PR, CI and independent PUBLIC release evidence

- Reviewed Bot_new_areazero/areazero-social-assets/AUTOMATION_PLAYBOOK.md, public operations, README and episode catalog; owner social OFF override supersedes old playbook social commands.
- Staged complete packages, including source, tests, safe/review fixtures, MIT license, source links, original logo, CI, README and SKILL.md, on **nondefault** portfolio branch `skill-lab/ep16-2026-11-09-hpa-service`, head commit `082a01950d1fac42f85fd5149c9a418f3fdf261e`. Portfolio `main` never contains these skill source directories.
- Extended existing four repository requests without removing them in [Bot provisioning PR #3](https://github.com/Kanompung1988/Bot_new_areazero/pull/3), merged `2a4ac97d954017384eaf13e5fc0f2f5261ddd514`. [Authorized provisioning run #42549520987](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/42549520987) **SUCCESS**; checked correct owner, public visibility and main default for each target separately.
- [k8s-hpa-request-contract-audit](https://github.com/Kanompung1988/k8s-hpa-request-contract-audit): [merged PR #1](https://github.com/Kanompung1988/k8s-hpa-request-contract-audit/pull/1), PR head `be6d8497dacedb0474dc04d5760515a83299353b`; [PR CI #42549711713](https://github.com/Kanompung1988/k8s-hpa-request-contract-audit/actions/runs/42549711713) successful; verified public main SHA `cfd9b8f4b04c1899bf97f06022fde61804951db6`; [main CI #42549809750](https://github.com/Kanompung1988/k8s-hpa-request-contract-audit/actions/runs/42549809750) successful. **21 unit tests per Python version** plus safe/review CLI and frontmatter smoke, as shown by job logs and job steps.
- [k8s-service-backend-audit](https://github.com/Kanompung1988/k8s-service-backend-audit): [merged PR #1](https://github.com/Kanompung1988/k8s-service-backend-audit/pull/1), PR head `d407dfe6d16fc1bcc2c345f1499b5ad5d42c7692`; [PR CI #42549719800](https://github.com/Kanompung1988/k8s-service-backend-audit/actions/runs/42549719800) successful; verified public main SHA `cc0713909ed8100601d08a8b548b6f8af8b22057`; [main CI #42549816521](https://github.com/Kanompung1988/k8s-service-backend-audit/actions/runs/42549816521) successful. **21 unit tests per Python version**, safe/review CLI and frontmatter smoke.
- Both README.md and SKILL.md were read back from each actual default branch after merge; both public repositories have valid own CI. Original logo content is exactly copied from the previous Skill Lab logo blob.
- **Official `skills-ref` validator: NOT_RUN. Independent security review: NOT_RUN.** CI tests use synthetic cases and cannot assert real cluster safety. No production use or external endorsements are claimed.

## Distribution boundary

**GitHub: PUBLIC/PUBLISHED** after actual public-default-branch readback and CI. **Instagram: OFF | Facebook: OFF**; never created/scheduled/modified a Skill Lab social post. Existing social drafts and publication idempotency records untouched. **Daily AI Scout unchanged.**
