# AREAZERO Skill Lab — EP.11 candidate research, tests and release evidence

**Date:** 2026-11-04 (Asia/Bangkok) · **Code release:** PUBLIC, independently verified · **Skill Lab social:** OFF by owner override of 2026-10-25

## Editorial selection model
Score dimensions are utility (25), originality relative to the 20 previously released tools (20), Claude Code/Codex agent fit (15), feasibility (15), audience (10), reproducible demo/QA (10), communication (5). Maximum 100; publish only score >=85, actual executable tests passing, and public default-branch code plus CI verified. Scores are **internal editorial judgments**, not adoption measures or independent reviews. No quota-forced releases.

| Developer pain / candidate | Utility /25 | Distinctiveness /20 | Agent fit /15 | Feasible /15 | Audience /10 | Demo /10 | Communication /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PEP 735 dependency groups: ambiguous normalized names, invalid PEP 508 strings, missing/cyclic includes | 24 | 19 | 14 | 15 | 9 | 9 | 4 | **94** | RELEASE: independent Python dependency group checker |
| PostgreSQL RLS: policy present while protection disabled, owner bypass, PUBLIC/true predicates | 25 | 18 | 14 | 14 | 9 | 9 | 4 | **93** | RELEASE: independent PostgreSQL RLS policy DDL checker |
| NGINX reverse-proxy header inheritance can erase security headers in nested configuration | 23 | 15 | 13 | 13 | 8 | 8 | 4 | **84** | DEFER: complex inheritance and false positives require broader parser coverage |
| Docker Compose writable bind mounts may expose sensitive host paths | 23 | 12 | 13 | 14 | 9 | 8 | 4 | **83** | DEFER: overlaps existing Compose/Docker project audit set |
| npm lifecycle scripts execute unexpectedly on install, pack or publish | 22 | 14 | 12 | 13 | 8 | 9 | 4 | **82** | DEFER: semantics and false-positive policy need stronger coverage |
| GitHub artifact attestation verification/enforcement gaps | 23 | 12 | 12 | 13 | 9 | 8 | 4 | **81** | DEFER: signature and provenance validation require external authoritative verifier |
| Kubernetes securityContext privilege settings drift between workloads | 22 | 11 | 12 | 14 | 9 | 8 | 4 | **80** | DEFER: context-dependent admission; overlaps security-review skill set |
| Git submodule URLs and pinned commits may be assumed trustworthy without verification | 20 | 13 | 12 | 13 | 8 | 9 | 4 | **79** | DEFER: static URL inspection cannot establish source trust |

## Primary-source technical references
1. [PEP 735 dependency groups specification](https://packaging.python.org/en/latest/specifications/dependency-groups/) and [PEP 735](https://peps.python.org/pep-0735/).
2. [PostgreSQL Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html); [CREATE POLICY](https://www.postgresql.org/docs/current/sql-createpolicy.html).
3. [NGINX proxy_set_header and configuration inheritance](https://nginx.org/en/docs/http/ngx_http_proxy_module.html).
4. [Docker Compose service mounts](https://docs.docker.com/reference/compose-file/services/).
5. [npm lifecycle scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/).
6. [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations).
7. [Kubernetes securityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/).
8. [gitmodules manual](https://git-scm.com/docs/gitmodules.html).

## Verified release evidence (2026-11-04)
- **Repo provisioner**: [GitHub Actions run 41758699690 — SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/41758699690); source stage on non-default portfolio branch `skill-lab/ep11-2026-11-04-rls-dependency-groups`; manifest update `369160419e3e5c77d40b4982f34294f1c0edbfd3`.
- **Python Dependency Group Audit**: [PUBLIC repository](https://github.com/Kanompung1988/py-dependency-group-audit); [merged PR #1](https://github.com/Kanompung1988/py-dependency-group-audit/pull/1); [final-head PR CI SUCCESS](https://github.com/Kanompung1988/py-dependency-group-audit/actions/runs/41759099227); [post-merge main CI SUCCESS](https://github.com/Kanompung1988/py-dependency-group-audit/actions/runs/41759153448); final main commit `5cab6fcf6e875bfb4ec54380c6047f5581f5ed07`. Independent 25/25 unit tests + safe/review fixture CLI checks on both Python 3.10 and 3.12, confirmed GitHub Actions.
- **PostgreSQL RLS Policy Audit**: [PUBLIC repository](https://github.com/Kanompung1988/pg-rls-policy-audit); [merged PR #1](https://github.com/Kanompung1988/pg-rls-policy-audit/pull/1); [final-head PR CI SUCCESS](https://github.com/Kanompung1988/pg-rls-policy-audit/actions/runs/41759103222); [post-merge main CI SUCCESS](https://github.com/Kanompung1988/pg-rls-policy-audit/actions/runs/41759161864); final main commit `a74b285dca904507d72887c7c4736c395d7664b2`. Independent 26/26 unit tests + safe/review fixture CLI checks on Python 3.10 and 3.12, confirmed GitHub Actions.
- Both independent repo default branches were read back: README.md and SKILL.md confirmed. Exact official Area Zero logo file was preserved from owner repository (`public/logo-full.svg`, Git blob `e1d2a0686010b251a530f9ad7eaf9afddf6a706b`).
- PR CI used current Node 24-based `actions/checkout@v6` and `actions/setup-python@v6`. Standalone docs contain synthetic fixtures, original hero SVG, README, contributor instructions, MIT code licensing and honest limitations.

## Safety, uncertainty and social restriction
- Python group audit is a static PEP 735 declaration checker; it never resolves, installs or queries package indexes. Its 'clear' result is not a successful dependency install.
- PostgreSQL RLS audit is a static **supplied-input-only** DDL reviewer, not a full PostgreSQL SQL parser or live effective-permission evaluator. It does not inspect database owners, roles/BYPASSRLS, catalogs, grants, policies in other migrations or actual tenant data.
- No independent audit, real-world user metrics, completeness/security guarantee or third-party review claimed. **Official skills-ref validator NOT_RUN**; internal Python 3.13 tests and public GitHub Actions Python 3.10/3.12 run, with public CI as canonical release gate.
- **Skill Lab Instagram and Facebook OFF**. No new posts, schedules, edits or social publishing calls. Daily AI Scout unchanged.
