# AREAZERO Skill Lab EP.07 — developer problem screen (2026-10-31)

**Editorial date:** Saturday, 31 October 2026 (Asia/Bangkok). **Objective:** choose up to TWO genuinely reusable, independently tested Agent Skills; a score of 85/100 is a necessary editorial threshold, not a promise to publish. **Social:** OFF under the 2026-10-25 owner override. No Instagram/Facebook publishing or scheduling is authorized.

## Dedupe and scoring method

Reviewed existing public portfolio: 12 standalone skills through EP.06 cover OpenAPI compatibility, CI log triage, GitHub Actions trust boundaries, environment variable contracts, PostgreSQL migrations, Docker build context, Python artifact packaging, Kubernetes RBAC, Terraform plans, Kubernetes NetworkPolicy scope, CODEOWNERS review coverage, and Kubernetes image pinning. This selection avoids reproducing those scanners. The scored candidates are practical workflows informed by first-party technical documentation, **not** evidence that a vendor incident occurred or that the author has discovered a vulnerability.

Score components: utility /25; distinction from already-released tools /20; agent-assisted fit /15; safe offline feasibility /15; audience /10; reproducibility/testability /10; communication value /5. Scores below are internal engineering judgments, not market research, adoption data or third-party validation. A passing test is necessary but not sufficient: code coverage, source accuracy, false-positive controls and public CI all matter.

| Practical developer pain point | Utility | Distinct | Agent fit | Feasible | Audience | Tests | Story | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Docker Compose `ports: "5432:5432"` and `ports: "8080:80"` bind all host interfaces by default, and explicit host mode bypasses Compose port mapping. A review should distinguish public/default, loopback, LAN, dynamic interpolation and unsupported ranges. | 24 | 18 | 15 | 14 | 9 | 10 | 5 | **95** | **BUILD** `compose-port-exposure-audit`; not a network scan. [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/) and [Compose ports](https://docs.docker.com/reference/compose-file/services/). |
| Helm charts reference `.Values.foo.bar` after defaults change; missing values may be intentional overrides, fallbacks or required inputs. A useful pre-merge check reports static paths and abstains on dynamic expressions. | 23 | 18 | 15 | 14 | 9 | 10 | 5 | **94** | **BUILD** `helm-values-contract-audit`; not a template renderer. [Helm Values files](https://docs.helm.sh/docs/v3/chart_template_guide/values_files/) and [default pipeline](https://docs.helm.sh/docs/chart_template_guide/functions_and_pipelines/). |
| Kubernetes Pod/container `securityContext` is absent or inadvertently permits privilege escalation. A complete audit would need policy-version and context-specific scope, not another generic YAML grep. | 23 | 15 | 14 | 10 | 9 | 9 | 4 | **84** | DEFER; close to existing Kubernetes security skills and below quality threshold. [Kubernetes security contexts](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/). |
| GitHub deployment environment name exists in a YAML workflow while human reviewer assumes required reviewers/branch restrictions. GitHub settings API context is mandatory to validate protection. | 23 | 16 | 13 | 8 | 9 | 9 | 4 | **82** | DEFER: cannot infer deployment gate enforcement from YAML alone. [GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments). |
| npm lifecycle hooks execute during dependency changes, potentially against a project's own install policy; robust detection needs precise npm version/workspace semantics. | 22 | 14 | 14 | 11 | 8 | 8 | 4 | **81** | DEFER: false-positive risk for legitimate scripts. [npm install-scripts](https://docs.npmjs.com/cli/v11/commands/npm-install-scripts/). |
| Git submodule pin changes or URL drift go unnoticed in code review. A trustworthy detector should distinguish local metadata from upstream commit provenance. | 20 | 15 | 12 | 13 | 8 | 8 | 4 | **80** | DEFER: policy and remote provenance needed. [Git submodule](https://git-scm.com/docs/git-submodule). |
| OpenTelemetry semantic convention renames silently alter dashboards/alerts. Correct detection requires version-specific semantic schemas and instrumentation versions. | 21 | 14 | 13 | 8 | 8 | 9 | 4 | **77** | DEFER: insufficient versioned fixture confidence. [OpenTelemetry semconv](https://opentelemetry.io/docs/specs/semconv/non-normative/code-attrs-migration/). |
| Dependabot grouped updates create unexpectedly broad PRs and may conflict with release compatibility policy. Robust judgment requires repo-specific dependency graph and policy. | 20 | 14 | 13 | 11 | 9 | 9 | 4 | **80** | DEFER: not enough differentiation from established dependency tooling. [Dependabot grouping](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference). |

## Engineering acceptance gates

### Compose Port Exposure Audit — 95/100 (editorial)

- Standalone slug: `compose-port-exposure-audit`; no overlap with `docker-context-guard` (build-context leakage). It reads only local Compose YAML, never runs Docker or network probes.
- Detect `PUBLIC_BIND` and `DATA_PORT_PUBLIC_BIND`, plus `HOST_NETWORK`; treat explicit non-loopback interface as informational and dynamic/ranged ports as unresolved, **not** safe.
- Local Python 3.13 regression tests: **30/30 PASSED**; safe/review CLI synthetic fixture exit codes and JSON verified. Official skills-ref validator: **NOT_RUN**. External review: **NOT_RUN**.
- CI on Python 3.10 and 3.12, PR merge evidence, public `main` files and SHA must be verified before claiming published.

### Helm Values Contract Audit — 94/100 (editorial)

- Standalone slug: `helm-values-contract-audit`; no prior Helm-focused skill. Scans local `values.yaml` and chart `templates/` with documented limits; parses literal `.Values.foo.bar` and `index .Values "foo"` references.
- Missing defaults are `REVIEW` **not confirmed errors**, while `default`/`required` pipelines and dynamic lookups produce informational signals. Does not execute Helm/Go templates or resolve parent chart/overrides.
- Local Python 3.13 regression tests: **30/30 PASSED**; safe/review CLI synthetic fixture exit codes and JSON verified. Official skills-ref validator: **NOT_RUN**. External review: **NOT_RUN**.
- CI on Python 3.10 and 3.12, PR merge evidence, public `main` files and SHA must be verified before claiming published.

## GitHub publication evidence (complete only after verification)

Repository provisioning request: `Kanompung1988/Bot_new_areazero/.github/skill-lab/repository-requests.json` on `main` commit `91571a3448cf5be9faff7d88129cabccff7cee9c`.

Staging branch: `Kanompung1988/agent-skills/skill-lab/ep07-2026-10-31-staging` commit `0f917ada8424a6cf555ed7663637c0cef89a330d`. It is a non-default staging branch; source **there is not a standalone release**.

**Repository provisioner:** [successful run #41158031698](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/41158031698) for manifest commit `91571a3448cf5be9faff7d88129cabccff7cee9c`. Created both requested PUBLIC repositories only after verifying staging SKILL.md.

**Compose:** [public repository](https://github.com/Kanompung1988/compose-port-exposure-audit), [merged PR #1](https://github.com/Kanompung1988/compose-port-exposure-audit/pull/1) from checked head `64db0cdf24a9005d84578f955454d4c5ed396643`. Default-branch merge SHA `00c8c691d8b387bd7ecd854f5b0897c5dc21822a`; [post-merge main CI #41158191035](https://github.com/Kanompung1988/compose-port-exposure-audit/actions/runs/41158191035): SUCCESS with Python 3.10 and 3.12 jobs. Root SKILL.md and README read back from public main.

**Helm:** [public repository](https://github.com/Kanompung1988/helm-values-contract-audit), [merged PR #1](https://github.com/Kanompung1988/helm-values-contract-audit/pull/1) from checked head `9562dd275fe3c3e2a3104b494e2d22fc2056af86`. Default-branch merge SHA `5fa58de7daf010f9d75cdf8fcf352c2f0a74796c`; [post-merge main CI #41158196325](https://github.com/Kanompung1988/helm-values-contract-audit/actions/runs/41158196325): SUCCESS with Python 3.10 and 3.12 jobs. Root SKILL.md and README read back from public main.

Both standalone repositories contain source, README, SKILL.md, fixtures, tests, CI, MIT code license and the exact official owner logo blob SHA `e1d2a0686010b251a530f9ad7eaf9afddf6a706b` (brand excluded from MIT). **Official skills-ref validator and external independent review: NOT_RUN.**

## Social and credibility boundary

Social publishing **OFF**. No new Metricool or Instagram/Facebook write is permitted. A successful static analysis test does **not** certify real production safety, Helm template correctness, Internet reachability, security compliance or the absence of vulnerabilities.
