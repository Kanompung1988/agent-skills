# AREAZERO Skill Lab — EP.09 candidate research (2026-11-02)

**Editorial boundary:** The selected tools are bounded, read-only local static checks for commonly missed configuration contracts. Eight topics were screened against the 16 existing public Skill Lab repositories as of 2026-11-02. A high score is an internal editorial rubric, **not** a measure of user adoption or independently certified security. Skills qualify only after real local tests and GitHub CI.

Score allocation: **utility 25, novelty vs current portfolio 20, Claude Code/Codex fit 15, feasibility 15, audience 10, demonstrability 10, communication 5**.

| # | Developer pain / proposed solution | U/25 | N/20 | Fit/15 | F/15 | A/10 | QA/10 | C/5 | Total | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Docker Compose starts a dependency but its application is not ready; audit `depends_on`, healthcheck, cycles and missing service | 23 | 18 | 14 | 14 | 9 | 9 | 5 | **92** | **BUILD** `compose-startup-readiness-audit` |
| 2 | Python packages install without a working CLI because of malformed `project.scripts`, duplicate commands or entry-point reference errors | 22 | 17 | 14 | 14 | 9 | 9 | 5 | **90** | **BUILD** `python-entrypoint-contract-audit` |
| 3 | Kubernetes PodDisruptionBudget unintentionally blocks drain or permits too many simultaneous evictions | 23 | 15 | 13 | 10 | 8 | 7 | 3 | 79 | defer; actual eligibility depends on workload and cluster status |
| 4 | npm install/CI lifecycle scripts execute unexpected package commands | 21 | 13 | 14 | 12 | 8 | 7 | 4 | 79 | defer; static command heuristics risk noise and existing security work overlaps |
| 5 | Git submodules track unexpected URLs or paths, complicating provenance and clone security | 19 | 16 | 12 | 11 | 7 | 6 | 3 | 74 | defer; requires robust Git index/gitlink handling beyond .gitmodules |
| 6 | GitHub Actions environments may allow deployment without required reviewers or branch restrictions | 23 | 12 | 13 | 8 | 8 | 5 | 4 | 73 | defer; accurate evaluation requires authenticated live protection config |
| 7 | GitHub artifact attestation exists but provenance verification is missing from release checks | 22 | 12 | 14 | 6 | 9 | 5 | 4 | 72 | defer; cryptographic verifier needs official tooling/trust roots |
| 8 | Helm values.schema.json and runtime overrides drift, causing rejected Chart upgrades | 20 | 10 | 13 | 12 | 8 | 8 | 4 | 75 | defer; existing Helm Values Contract skill is adjacent |

## Primary references and boundaries

1. Docker Compose services and `depends_on` conditions: https://docs.docker.com/reference/compose-file/services/ ; startup-order explanation: https://docs.docker.com/compose/how-tos/startup-order/ . `service_started` does not imply application readiness. Complete multi-file Compose context and image-level healthchecks remain out of scope.
2. PyPA pyproject specification: https://packaging.python.org/en/latest/specifications/pyproject-toml/ ; entry points spec: https://packaging.python.org/en/latest/specifications/entry-points/ . Reserved groups and `module:object` grammar can be checked without importing arbitrary code; dynamic build metadata and generated files cannot.
3. Kubernetes PDB reference: https://kubernetes.io/docs/tasks/run-application/configure-pdb/ . Scaling and active Pod disruption budgets require runtime context.
4. npm lifecycle scripts: https://docs.npmjs.com/using-npm/scripts.html/ . Treat script existence as contextual, not an exploit by itself.
5. Git .gitmodules specification: https://git-scm.com/docs/gitmodules . Relative URLs and recorded gitlinks must be handled carefully.
6. GitHub deployment environment protection: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments . Workflow YAML alone cannot confirm required reviewers and branch gates.
7. GitHub artifact attestation offline verification: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline . Do not implement fake signature verification.
8. Helm chart values schema: https://helm.sh/docs/topics/charts/ . Helm validates final merged `.Values` rather than defaults only.

## Verification / release gate

| Required check | Local evidence (2026-11-02) | Public release evidence |
|---|---|---|
| Compose startup audit | 26/26 unittest, clean fixture 0 findings, risky fixture 4 findings, strict exit 1 | [Public `main` CI: SUCCESS on Python 3.10/3.12](https://github.com/Kanompung1988/compose-startup-readiness-audit/actions/runs/41376691671) |
| Python entry-point audit | 28/28 unittest, clean fixture 0, review fixture 3 findings, strict exit 1 | [Public `main` CI: SUCCESS on Python 3.10/3.12](https://github.com/Kanompung1988/python-entrypoint-contract-audit/actions/runs/41376699733) |
| Official `skills-ref` | NOT_RUN; unavailable locally | NOT_RUN |
| Independent human review | NOT_RUN | NOT_RUN |
| Social distribution | OFF by owner override since 2026-10-25 | OFF (never schedule or publish) |

## Verified independent public releases — 2026-11-02

### Compose Startup Readiness Audit — 92/100
- Repository: https://github.com/Kanompung1988/compose-startup-readiness-audit
- Feature PR #1: https://github.com/Kanompung1988/compose-startup-readiness-audit/pull/1 ; original README hero PR #2: https://github.com/Kanompung1988/compose-startup-readiness-audit/pull/2
- Verified public `main` SHA: `49a4481bfb0261faf479dc20a337612e4750db94`
- Latest `main` CI run https://github.com/Kanompung1988/compose-startup-readiness-audit/actions/runs/41376691671 : SUCCESS, Python 3.10 and 3.12 test jobs each SUCCESS.
- Local unit tests 26/26; safe/review CLI fixture runs tested.

### Python Entry-point Contract Audit — 90/100
- Repository: https://github.com/Kanompung1988/python-entrypoint-contract-audit
- Feature PR #1: https://github.com/Kanompung1988/python-entrypoint-contract-audit/pull/1 ; original README hero PR #2: https://github.com/Kanompung1988/python-entrypoint-contract-audit/pull/2
- Verified public `main` SHA: `344b7f1f88a434486c493afe55c147d9305ec3aa`
- Latest `main` CI run https://github.com/Kanompung1988/python-entrypoint-contract-audit/actions/runs/41376699733 : SUCCESS, Python 3.10 and 3.12 test jobs each SUCCESS.
- Local unit tests 28/28; safe/review CLI fixture runs tested.

Both public default branches expose `SKILL.md`, complete README, original hero illustration, source, tests, synthetic examples, MIT license, CI, and byte-for-byte upstream AREA ZERO logo (Git blob SHA `e1d2a0686010b251a530f9ad7eaf9afddf6a706b`). The owner-supplied logo is not covered by the MIT code license. Repo provisioning workflow https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/41376096675 completed SUCCESS.

**Verification limits:** The official `skills-ref` validator and an independent external review were NOT_RUN. Local fixtures and passing CI do not guarantee every runtime failure or package manager nuance is detected.

**Skill Lab social: OFF.** No Instagram or Facebook post created, scheduled, modified, or published in this run. Daily AI Scout remains independent.