# AREAZERO Skill Lab EP.08 — eight developer pain points (2026-11-01)

**Editorial date:** Sunday, 1 November 2026, Asia/Bangkok. **Project objective:** create at most TWO reusable, tested, unique Agent Skills; editorial score **>=85/100** is necessary, but actual test + PR + public-main CI are also required. **Social:** OFF under the owner override of 2026-10-25. No Skill Lab Instagram or Facebook write is authorized.

## Dedupe and score rubric

Checked the public portfolio and EP.01–EP.07 catalogue (14 standalone repos): OpenAPI, CI logs, GitHub Actions trust boundaries, env contracts, PostgreSQL migrations, Docker context, Python artifact archives, Kubernetes RBAC, Terraform plans, Kubernetes NetworkPolicy, CODEOWNERS, Kubernetes image pins, Compose port publishing, Helm values contracts. EP.08 intentionally studies **AWS IAM OIDC role trust JSON**, not GitHub Actions workflow YAML, and **Node.js exported package entrypoints**, not Python package archives.

Rubric: utility /25, distinction /20, Claude Code/Codex fit /15, safe feasibility /15, developer audience /10, reproducible tests /10, shareable clarity /5. These are **internal editorial judgments**, not quantitative market measurements, evidence of novel invention, adoption, security compliance or an independent audit. Official sources below define the technical pain points; none imply an actual incident.

| Developer pain point and rationale | Utility | Distinct | Agent fit | Feasible | Audience | Tests | Clarity | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AWS IAM OIDC trusts can accept unintended GitHub repository identities or branches when `sub`/`aud` conditions are absent or too broad. Review the **role trust-policy JSON**, not workflow YAML. [AWS identity provider guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html). | 24 | 19 | 14 | 14 | 9 | 10 | 5 | **95** | **BUILD** `aws-github-oidc-trust-audit` |
| Node.js `exports` maps may contain invalid path targets, mixed conditions/subpaths, unsafe segments and unbuilt artifact paths. Inspect metadata without running npm lifecycle scripts. [Node.js packages documentation](https://nodejs.org/api/packages.html) and [npm package metadata](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/). | 23 | 18 | 15 | 14 | 9 | 10 | 5 | **94** | **BUILD** `npm-export-map-audit` |
| Docker Compose `depends_on` only waits for process start in short syntax; startup readiness requires explicit health semantics. Adjacent to current Compose tooling and cross-service behavior needs context. [Docker Compose startup order](https://docs.docker.com/compose/how-tos/startup-order). | 22 | 14 | 14 | 13 | 8 | 9 | 4 | **84** | DEFER; below gate |
| Kubernetes PDB selectors and percentage budgets can unintentionally block or permit eviction. Real impact requires matching workload replicas/controllers and version semantics. [Kubernetes PDB docs](https://kubernetes.io/docs/tasks/run-application/configure-pdb/). | 22 | 15 | 12 | 12 | 8 | 9 | 4 | **82** | DEFER; runtime context |
| Python `pyproject.toml` console entrypoint references can drift from available modules/functions. Static existence checks might miss generated code or dynamic attributes. [Python packaging entrypoints](https://packaging.python.org/en/latest/specifications/entry-points/). | 21 | 13 | 14 | 13 | 9 | 9 | 3 | **82** | DEFER; narrower impact |
| NGINX reverse proxy headers may accidentally alter expected upstream host/client IP. Correct analysis needs include/inheritance and trusted proxy configuration. [NGINX reverse proxy guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy). | 21 | 13 | 13 | 10 | 8 | 9 | 4 | **78** | DEFER; false-positive risk |
| GitHub environment required reviewers and branch protection cannot be established by workflow YAML alone; requires environment settings, role/plan visibility and current rules. [GitHub deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments). | 22 | 13 | 12 | 8 | 9 | 9 | 4 | **77** | DEFER; unverified external policy |
| Git submodule URL/revision changes can hide in code review; true provenance needs gitlink metadata, worktree state and remote confirmation. [git-submodule manual](https://git-scm.com/docs/git-submodule). | 20 | 13 | 12 | 12 | 8 | 9 | 4 | **78** | DEFER; source verification needs care |

## Selected skill engineering evidence

### 1. AWS GitHub OIDC Trust Audit (95/100 editorial)
- Dedicated **PUBLIC** repository: https://github.com/Kanompung1988/aws-github-oidc-trust-audit
- Source semantics: offline JSON IAM trust-policy analysis, GitHub OIDC `Principal.Federated`, `AssumeRoleWithWebIdentity`, positive `StringEquals`/`StringLike` restrictions for `sub`/`aud`. HIGH vs REVIEW findings; refuses duplicate JSON keys, symlink input, files >2 MB, >100 JSON files; does not echo subject literal values.
- PR https://github.com/Kanompung1988/aws-github-oidc-trust-audit/pull/1 merged from final tested feature head `c373950a3dfffc6448dfc1203856bcfd4aa132a8` to public `main` commit `4027df6c73d6438b7ceea1978cc81229d44ee319`.
- **Actual CI:** [PR Python 3.10/3.12 jobs SUCCESS](https://github.com/Kanompung1988/aws-github-oidc-trust-audit/actions/runs/41263845434), [post-merge public-main Python 3.10/3.12 SUCCESS](https://github.com/Kanompung1988/aws-github-oidc-trust-audit/actions/runs/41263922125). GitHub job logs show **27 unit/CLI tests PASSED per Python version**, plus separate synthetic safe/review CLI smoke and metadata/logo checks.
- Regression review included `sts:*` wildcard actions and case-insensitive action representation; fixing those before merge is evidence of internal self-review, **not independent external review**.
- LIMITS: static signals cannot prove an IAM role is currently assumable, account effective permissions, GitHub environment restrictions or production exploitability. Official `skills-ref` validator: **NOT_RUN**. Independent external security review: **NOT_RUN**.

### 2. npm Export Map Audit (94/100 editorial)
- Dedicated **PUBLIC** repository: https://github.com/Kanompung1988/npm-export-map-audit
- Reads `package.json` without executing Node/npm or network calls. Checks relative `exports` target paths, traversal/dot/node_modules/encoded separator targets, mixing condition/subpath map keys, optional built-file existence, and marks wildcard patterns as requiring separate Node resolution.
- PR https://github.com/Kanompung1988/npm-export-map-audit/pull/1 merged from final tested head `1780d8119593ede9abf447eadd84b133e339dbf7` to public `main` commit `21249fee29baef081357889c88c9e774a74892ee`.
- **Actual CI:** [PR Python 3.10/3.12 jobs SUCCESS](https://github.com/Kanompung1988/npm-export-map-audit/actions/runs/41263862966), [post-merge public-main Python 3.10/3.12 SUCCESS](https://github.com/Kanompung1988/npm-export-map-audit/actions/runs/41263928023). GitHub logs show **32 unit/CLI tests PASSED per Python version**, plus safe/review fixture smoke and exact-logo verification.
- Regression review added percent-encoded forward slash and backslash cases before the final CI. Actual runtime exports compatibility still requires Node and trusted release checks.
- LIMITS: not a Node module resolver, npm artifact auditor, runtime package compatibility guarantee or external security audit. Official `skills-ref` validator: **NOT_RUN**. Independent reviewer: **NOT_RUN**.

### Repository automation, idempotency and provenance

1. Public portfolio staging branch `skill-lab/ep08-2026-11-01-staging` contains complete two-skill packages and was synchronized to final tested source at commit `42c3a936d3a0e5edfcb997d051529049ba7f2710`. Staging does **not** count as the release.
2. Provisioning manifest in `Bot_new_areazero/main` preserved all 14 historical repository requests verbatim in `.github/skill-lab/history/2026-10-31-requests.json`, then set the bounded current manifest to exactly two new slugs with `source_ref`. [Bot provisioning PR #1 merged](https://github.com/Kanompung1988/Bot_new_areazero/pull/1) to SHA `f1618d444c3a233011ce69492e1e082264a7e620`.
3. [Provisioner run #41263665107 SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/41263665107) created/verified the two PUBLIC repositories before code PRs. Repo creation does not imply successful CI or release.
4. Each dedicated repo has its own `SKILL.md`, README, Python CLI, tests, synthetic fixtures, primary references, CI, MIT code license, safety/contributor documentation and original SVG hero. The exact official Area Zero logo blob SHA is `e1d2a0686010b251a530f9ad7eaf9afddf6a706b`; logo is not MIT-licensed.
5. GitHub code release and current two-version CI were checked on each PUBLIC default branch independently. The portfolio is an index only, not the source monorepo.

## Publication boundaries

**GitHub code: PUBLIC after main readback and CI success.** **Skill Lab social: OFF.** No Metricool create, schedule, update, publish, IG or FB social workflow actions were invoked. The separate Daily AI Scout was not changed.

These are open-source static review helpers, not proof of live protection or external adoption. Scores reflect internal engineering prioritization; CI is reproducible technical evidence, not an independent audit.
