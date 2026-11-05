# AREAZERO Skill Lab — EP.12 research, QA and release evidence

**Date:** 2026-11-05 (Asia/Bangkok) · **Skill Lab code release:** PUBLIC, independently re-read after merge · **Social:** OFF by user override since 2026-10-25.

## Evaluation methodology

Scores are internal editorial decisions, NOT community ratings, benchmarks or external reviews. We score **utility /25**, **originality relative to 22 prior tools /20**, **Claude Code/Codex fit /15**, **implementable scope /15**, **developer audience /10**, **deterministic tests /10**, **explainability /5**. Release threshold: >=85/100 plus actual tests and CI and a verified PUBLIC default-branch release. This run deliberately considered previously deferred topics with clarified technical scope but avoided repeating already released functions.

| Concrete developer pain point | Utility /25 | Originality /20 | Agent fit /15 | Feasible /15 | Audience /10 | QA /10 | Explain /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NGINX nested add_header can unexpectedly erase inherited security headers; version-dependent merge inheritance | 24 | 19 | 14 | 14 | 9 | 10 | 4 | **94** | RELEASE bounded context inheritance checker |
| npm ci/install/pack can execute package.json lifecycle hooks and implicit node-gyp fallback | 24 | 18 | 14 | 14 | 9 | 9 | 4 | **92** | RELEASE bounded script-policy checker |
| GitHub reusable workflow permission and secrets boundary propagation | 22 | 15 | 13 | 13 | 8 | 9 | 4 | **84** | DEFER near overlap with GHA Trust Boundary; needs cross-file proof |
| Docker Compose writable host bind mounts | 22 | 12 | 13 | 14 | 9 | 8 | 4 | **82** | DEFER overlaps 3 existing Docker/Compose analyzers |
| Kubernetes workload securityContext drift | 22 | 11 | 13 | 14 | 9 | 8 | 4 | **81** | DEFER requires cluster admission context |
| GitHub artifact-attestation verification gaps | 21 | 12 | 12 | 13 | 9 | 9 | 4 | **80** | DEFER external authoritative verifier needed |
| Git submodule URL/pin trust assumptions | 20 | 13 | 12 | 13 | 8 | 9 | 4 | **79** | DEFER URL/pin alone does not establish provenance |
| Helm values override-vs-default contract | 20 | 11 | 12 | 13 | 9 | 8 | 4 | **77** | DEFER overlap Helm Values Contract tool |

## Primary technical sources (checked 2026-11-05)

1. [NGINX ngx_http_headers_module: add_header and add_header_inherit, 1.29.3](https://nginx.org/en/docs/http/ngx_http_headers_module.html).
2. [npm CLI v11 Scripts: install/ci/pack/publish lifecycle order, prepublish and binding.gyp](https://docs.npmjs.com/cli/v11/using-npm/scripts/).
3. [GitHub reusable workflows: inputs, secrets and nesting](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
4. [Docker Compose Services: binds and volumes](https://docs.docker.com/reference/compose-file/services/).
5. [Kubernetes securityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/).
6. [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations).
7. [Git submodule configuration](https://git-scm.com/docs/gitmodules.html).
8. [Helm values files](https://helm.sh/docs/chart_template_guide/values_files/).
9. [Agent Skills specification](https://agentskills.io/specification).

## Verified provenance and QA (2026-11-05)

- Source staged on **nondefault** portfolio branch `skill-lab/ep12-2026-11-05-header-npm` under `skills/<slug>/`, without merging source folders into portfolio main.
- Authorized repository manifest updated at `Bot_new_areazero/main` commit `c99289956ad8c8ed0764e76653cddbc8e0fe926d`. [GitHub Actions provisioner SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/41952467239). Explicitly does not grant Skill Lab social posting.
- **NGINX Header Inheritance Audit**: [PUBLIC repo](https://github.com/Kanompung1988/nginx-header-inheritance-audit), [merged PR #1](https://github.com/Kanompung1988/nginx-header-inheritance-audit/pull/1); [PR CI success](https://github.com/Kanompung1988/nginx-header-inheritance-audit/actions/runs/41952684843) on final PR head `f8c4a4d615b8f9d83febcc9066b9873eda07af2d`; [main CI success](https://github.com/Kanompung1988/nginx-header-inheritance-audit/actions/runs/41952808524) on public main commit **`b0b5910fca6e78e9486c55492ec0ef56db6a75ed`**. **26/26 Python unit tests** + safe/review fixture smoke passed on BOTH Python 3.10 and 3.12, confirmed from GitHub Actions job logs. Public main `SKILL.md`, README, own CI file read back.
- **npm Lifecycle Script Policy Audit**: [PUBLIC repo](https://github.com/Kanompung1988/npm-lifecycle-policy-audit), [merged PR #1](https://github.com/Kanompung1988/npm-lifecycle-policy-audit/pull/1); [PR CI success](https://github.com/Kanompung1988/npm-lifecycle-policy-audit/actions/runs/41952688511) on final PR head `b2d0f9a9ea694e58cc175fa5b66452acee10fcea`; [main CI success](https://github.com/Kanompung1988/npm-lifecycle-policy-audit/actions/runs/41952826099) on public main commit **`c78a02f1e3c5baa9f2bd1a0870070e2c2d10f81b`**. **27/27 Python unit tests** + safe/review fixture smoke passed on BOTH Python 3.10 and 3.12, confirmed from GitHub Actions job logs. Public main `SKILL.md`, README, own CI file read back.
- Each skill ships full Agent Skills metadata/instructions, Python source, examples, rule references, fixture tests, MIT source license, original hero, exact official unchanged SVG owner logo, installation docs for Claude Code and Codex, and read-only CLI exit/status contracts.
- **Official `skills-ref` validator: NOT_RUN.** GitHub CI includes frontmatter smoke only, not full third-party format validation. No independent external audit, production deployment validation, real user metrics, or full security claim.

## Interpretation and boundaries

- NGINX audit is a local lexical + nested-context model, not the nginx parser: no include expansion, dynamic module logic, actual virtual-server selection or live TLS/HTTP verification. Operator should run `nginx -t` and stage-response checks.
- npm audit reads one provided local `package.json`; it maps recognized lifecycle event names and `binding.gyp` presence but does not execute the commands, evaluate command intent, recursively inspect workspaces or analyze transitive dependency scripts. A lifecycle hook can be legitimate.
- **Social status: OFF.** No Metricool create/update/schedule calls, no Skill Lab social workflows, and no changes to existing Skill Lab posts/drafts. Daily AI Scout unchanged.
