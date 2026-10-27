# EP.03 developer pain-point research — 2026-10-27

**Scope:** Eight distinct developer problems screened against four previously released AREAZERO Skill Lab tools. Source links are primary technical references; they establish that the *underlying technical issue exists*, not frequency, market size, novelty, or external adoption. Dates here refer to the **editorial review date**, not alleged dates of new product launches.

**Scoring:** Practical utility /25, distinctiveness from existing tools /20, Claude Code & Codex fit /15, feasibility /15, developer audience /10, reproducible demonstration and tests /10, communication usefulness /5 = **100**. Scores are internal subjective editorial estimates, not third-party validation. Minimum to build: **85/100**, max two selected.

| Pain point | Practical /25 | Distinct /20 | Agent fit /15 | Feasible /15 | Audience /10 | Tests /10 | Share /5 | Total /100 | Decision | Primary source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| PostgreSQL migration lock/data-loss risks | 24 | 18 | 15 | 15 | 9 | 10 | 5 | **96** | SELECT — `pg-migration-risk-audit` | [docs](https://www.postgresql.org/docs/current/sql-altertable.html) |
| Docker context / secret-path leakage and broad COPY | 24 | 17 | 15 | 15 | 9 | 10 | 5 | **95** | SELECT — `docker-context-guard` | [docs](https://docs.docker.com/build/concepts/context/) |
| Kubernetes liveness/readiness probe confusion | 22 | 13 | 14 | 10 | 9 | 8 | 4 | **80** | DEFER — cluster-specific context and existing upstream guidance | [docs](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/) |
| npm lockfile mismatch and non-reproducible CI installs | 21 | 11 | 15 | 13 | 9 | 10 | 5 | **84** | DEFER — overlaps mature `npm ci` checks; needs new differentiator | [docs](https://docs.npmjs.com/cli/v11/commands/npm-ci/) |
| Terraform state/plan sensitive values | 24 | 12 | 14 | 9 | 9 | 6 | 3 | **77** | DEFER — cannot safely claim complete secret-leak detection | [docs](https://developer.hashicorp.com/terraform/language/manage-sensitive-data) |
| OpenTelemetry trace context breaks across services | 21 | 15 | 15 | 10 | 8 | 8 | 3 | **80** | DEFER — meaningful verification requires runtime signals | [docs](https://opentelemetry.io/docs/concepts/context-propagation/) |
| GitHub Actions OIDC claim / workflow trust-policy drift | 21 | 11 | 15 | 10 | 8 | 8 | 4 | **77** | DEFER — partially overlaps existing GHA Trust Boundary Audit | [docs](https://docs.github.com/en/actions/reference/security/oidc) |
| Python requirements/constraints drift in CI | 20 | 12 | 14 | 13 | 9 | 9 | 3 | **80** | DEFER — needs reliable multi-tool resolver semantics | [docs](https://pip.pypa.io/en/stable/user_guide/) |

## Selection rationale

**1. PG Migration Risk Audit (96/100).** PostgreSQL migration reviews regularly need a quick *file-only* sweep for destructive DDL, broad writes, index locks and illegal concurrent-index transaction wrapping. Unlike the EP.01 OpenAPI audit, it targets SQL migration risk and never connects to a database. The [ALTER TABLE docs](https://www.postgresql.org/docs/current/sql-altertable.html) explain locking and dependencies; [CREATE INDEX docs](https://www.postgresql.org/docs/current/sql-createindex.html) cover write-blocking and CONCURRENTLY limits. [Repository](https://github.com/Kanompung1988/pg-migration-risk-audit) · [PR #1](https://github.com/Kanompung1988/pg-migration-risk-audit/pull/1) · [PR CI](https://github.com/Kanompung1988/pg-migration-risk-audit/actions/runs/40437637025).

**2. Docker Context Guard (95/100).** Docker context and `.dockerignore` precedence can accidentally leave secret-looking paths available to builds. The scanner checks filenames (not values), broad COPY/ADD and risky ARG/ENV names. [Docker context spec](https://docs.docker.com/build/concepts/context/) details precedence/negation, and [Docker secrets guidance](https://docs.docker.com/build/building/secrets/) favors secret mounts over ARG/ENV. [Repository](https://github.com/Kanompung1988/docker-context-guard) · [PR #1](https://github.com/Kanompung1988/docker-context-guard/pull/1) · [PR CI](https://github.com/Kanompung1988/docker-context-guard/actions/runs/40437682390).

## Actual release evidence, checked 2026-10-27

- **PG Migration Risk Audit:** PUBLIC `Kanompung1988/pg-migration-risk-audit`, root `SKILL.md` and `README.md` fetched successfully from `main` after PR #1 merged at commit `a555c4d2a5c5f7b7f3842345cffdf62fb08d7521`. On PR head `69c976d1cc8412ba333bd47233e6c760c3bcf059` GitHub Actions run 40437637025 completed SUCCESS with Python 3.10 and 3.12 jobs both green. Inspected job logs confirmed **33 unit tests passed per runtime**, plus safe/unsafe fixture CLI smoke checks in the same workflow.
- **Docker Context Guard:** PUBLIC `Kanompung1988/docker-context-guard`, root `SKILL.md` and `README.md` fetched successfully from `main` after PR #1 merged at commit `aac27112d23b25ff26bdd567ea211d3682574f0e`. PR head `f6af7c27249abaab7d49a9a8d3c23f9a84f5a5f0` GitHub Actions run 40437682390 completed SUCCESS, both Python 3.10 and 3.12 green. Inspected job logs confirmed **26 unit tests passed per runtime**, plus both fixture CLI smoke checks.
- Neither project requires access to actual secrets or production services. Rule-based scanners are intentionally partial; false positives and false negatives remain possible.
- External independent review: **NOT RUN**. Official `skills-ref` validation: **NOT RUN** (not installed or verifiably executed). Passing synthetic tests is not proof of production safety.
- **SOCIAL = OFF.** No Skill Lab Instagram/Facebook publishing, scheduling, or auto-reenable is authorized. Daily AI Scout is separate and unaffected.

## Duplicate rejection

Previously published: [OpenAPI Compatibility Audit](https://github.com/Kanompung1988/openapi-compat-audit), [CI Log Triage](https://github.com/Kanompung1988/ci-log-triage), [GHA Trust Boundary Audit](https://github.com/Kanompung1988/gha-trust-boundary-audit), [Env Contract Audit](https://github.com/Kanompung1988/env-contract-audit). These are not reissued or repackaged as today's new skills.
