# AREAZERO Skill Lab — EP.26 Candidate Research & Release Evidence

**Date:** 2026-11-19 (Asia/Bangkok) · **Public portfolio:** [agent-skills](https://github.com/Kanompung1988/agent-skills) · **Social:** OFF indefinitely, per owner instruction 2026-10-25. Daily AI Scout untouched.

This episode curates at most TWO standalone Agent Skills after actual source, tests, PR CI, post-merge `main` CI and public default-branch verification. Scores are editorial estimates, not measurements from customers.

## Eight concrete developer pain points

Rubric: utility (25), distinctiveness (20), relevance to Claude/Codex (15), build feasibility (15), audience (10), demonstrability (10), social shareability (5), total 100. Score >=85 is a *necessary* release gate, not a substitute for independent tests.

| Candidate | Utility | Unique | Agent | Feasible | Audience | Demo | Share | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PostgreSQL privileged SECURITY DEFINER `search_path` SQL shadowing | 24 | 20 | 14 | 14 | 9 | 9 | 4 | **94** | **RELEASED**, bounded local SQL review |
| GitHub Actions `upload-artifact` retention-day vs visibility/organization limits | 23 | 19 | 14 | 14 | 9 | 8 | 4 | **91** | **RELEASED**, with explicit operator inputs |
| Renovate lockfile maintenance schedule and regeneration surprises | 21 | 17 | 13 | 12 | 9 | 7 | 3 | **82** | Not qualified today; scheduler semantics need more coverage |
| Self-hosted runner label and group constraints that strand jobs | 21 | 16 | 12 | 12 | 9 | 7 | 3 | **80** | Not qualified; runner inventory and policy are dynamic |
| Sigstore keyless signing identity and OIDC issuer matching | 21 | 17 | 11 | 10 | 9 | 8 | 3 | **79** | Not qualified; demand strict real cryptographic evidence |
| Gateway API status `observedGeneration` vs applied route configuration | 20 | 17 | 12 | 11 | 8 | 7 | 3 | **78** | Not qualified; snapshot timing and controller differences |
| Helm OCI provenance verification and chart authenticity | 20 | 15 | 11 | 12 | 8 | 8 | 3 | **77** | Not qualified; overlapping provenance/trust mechanics |
| Argo Rollouts Analysis argument drift across templates | 18 | 7 | 13 | 13 | 9 | 9 | 4 | **73** | Not qualified; overlaps existing Argo Rollouts Analysis Audit |

**Additional duplicate rejection (not an eligible new Skill):** [compose-published-port-audit](https://github.com/Kanompung1988/compose-published-port-audit) is already a separately provisioned public repo with passing [CI](https://github.com/Kanompung1988/compose-published-port-audit/actions/runs/44444036487), but materially duplicates [compose-port-exposure-audit](https://github.com/Kanompung1988/compose-port-exposure-audit) (same Docker Compose `ports:`, public/default interfaces and read-only review task). It is deliberately **not added to this curated episode or counted as a new qualifying skill**, and its existing code, public repository and manifest record are preserved. Its existence is not denied. The repo-provisioning manifest therefore contains 27 preserved requests rather than assuming two additions and deleting the overlap.

## Accepted releases (independent, public `main`)

### 1. PostgreSQL SECURITY DEFINER Search Path Audit — 94/100

- Repository: https://github.com/Kanompung1988/pg-security-definer-path-audit
- [Release PR #1](https://github.com/Kanompung1988/pg-security-definer-path-audit/pull/1): merged. Post-merge `main` SHA: `bd29523ba1a886164e756a3194d8e2da04a9c5ab`.
- [PR CI](https://github.com/Kanompung1988/pg-security-definer-path-audit/actions/runs/44444004800) SUCCESS; [`main` CI](https://github.com/Kanompung1988/pg-security-definer-path-audit/actions/runs/44444095257) SUCCESS, Python 3.10/3.12 and 25 unit tests per version plus fixtures. Earlier [PR CI failure](https://github.com/Kanompung1988/pg-security-definer-path-audit/actions/runs/44443874038) was corrected before merge.
- Detects search-path hazards in local SQL scripts; **cannot infer live effective schemas, privileges, executable SQL safety or actual role access**.
- Primary authority: [PostgreSQL current `CREATE FUNCTION`, "Writing SECURITY DEFINER Functions Safely"](https://www.postgresql.org/docs/current/sql-createfunction.html).

### 2. GitHub Actions Artifact Retention Audit — 91/100

- Repository: https://github.com/Kanompung1988/gha-artifact-retention-audit
- [Release PR #1](https://github.com/Kanompung1988/gha-artifact-retention-audit/pull/1): merged. Post-merge `main` SHA: `6a70f99eb9676f82542b098352c3b61cedbf63af`.
- [PR CI](https://github.com/Kanompung1988/gha-artifact-retention-audit/actions/runs/44446253888) SUCCESS; [`main` CI](https://github.com/Kanompung1988/gha-artifact-retention-audit/actions/runs/44446337356) SUCCESS, Python 3.10/3.12, 30 unit tests per version plus safe/review CLI fixtures and metadata/logo integrity checks.
- Reviews local `actions/upload-artifact` calls, `retention-days`, public 90-day/private 400-day caps and explicitly supplied effective policy/minimum-review windows. `0` means repo default, not immediate deletion. Dynamic expressions require manual verification; the tool does not query GitHub.
- Primary authority: [GitHub Actions repository retention policy](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository), [custom per-artifact retention](https://docs.github.com/en/actions/tutorials/store-and-share-data). As of **2026-10-01**, retention settings also govern checks, workflow runs and commit statuses; this auditor targets `upload-artifact` steps, **not** those broader data categories.

## Repository provisioning and structure

- Provisioning through `Kanompung1988/Bot_new_areazero`: [PR #14](https://github.com/Kanompung1988/Bot_new_areazero/pull/14) and [PR #15](https://github.com/Kanompung1988/Bot_new_areazero/pull/15) merged. Latest [provisioning workflow](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/44445197838) SUCCESS.
- Source staged under `skills/<slug>/` on non-default branches `skill-lab/ep26-2026-11-19-pg-compose` and `skill-lab/ep26-2026-11-19-retention`, not on portfolio `main`.
- Each qualifying skill has its own root `SKILL.md`, English README, CLI, fixtures, references, MIT code LICENSE, original Area Zero logo SVG, Claude Code/Codex install instructions, and independent GitHub Actions.
- Agent Skills [specification](https://agentskills.io/specification) followed with custom metadata/frontmatter checks. Official `skills-ref validate` **NOT_RUN**; no external/production audit claimed.

**Code release:** PUBLISHED for the two curated repositories verified on public default `main`. **Social release:** OFF/DRAFT; no Instagram/Facebook publishing, scheduling, reactivation, Metricool writes or social-workflow changes. Daily AI Scout unaffected.
