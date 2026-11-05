<p align="center"><img src="assets/area-zero-logo-full.svg" alt="Original official Area Zero brand logo" width="270"></p>

<p align="center"><img src="assets/hero.svg" alt="AREAZERO Skill Lab: independent open-source Agent Skills with reproducible tests" width="100%"></p>

<h3 align="center">Make AI more useful every day — one tested open-source skill at a time.</h3>

<p align="center">An independent project for every Skill. A clear developer problem. Reproducible code and tests.<br>Built by <b>AREAZERO Skill Lab</b> for <b>Claude Code</b>, <b>Codex</b>, and open-source developers.</p>

<p align="center">
<a href="https://github.com/Kanompung1988/agent-skills/actions/workflows/validate-skills.yml"><img alt="Index QA status" src="https://github.com/Kanompung1988/agent-skills/actions/workflows/validate-skills.yml/badge.svg"></a>
<a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/Agent%20Skills-open%20spec-00D9FF?style=flat-square" alt="Agent Skills specification"></a>
<img src="https://img.shields.io/badge/independent%20skill%20repos-24-00FFA3?style=flat-square" alt="Twenty-four independent skills">
<a href="LICENSE"><img src="https://img.shields.io/badge/code%20license-MIT-0A1929?style=flat-square" alt="Code MIT License"></a>
</p>

<p align="center"><a href="#explore-the-skills"><b>Explore skills</b></a> &nbsp;·&nbsp; <a href="#how-to-install"><b>Install</b></a> &nbsp;·&nbsp; <a href="#how-we-work"><b>Our process</b></a> &nbsp;·&nbsp; <a href="docs/EPISODES.md"><b>Episodes</b></a> &nbsp;·&nbsp; <a href="docs/SKILL_LAB_OPERATIONS.md"><b>Automation contract</b></a></p>

> [!NOTE]
> **This repository is the portfolio and release index, not a monorepo of skills.** Each skill is independently maintained in its own PUBLIC GitHub repository, with its own README, source, CI, issues, stars and contributor activity. Follow the individual repository links below to install or report bugs.

## Why independent repositories?

Most developer problems deserve a focused tool, not a giant feature list. Independent projects let you inspect a small codebase, install only what you need, and follow the issues/releases that matter to you. For maintainers, every repository has a distinct CI history and contribution scope; this page is simply the discovery layer.

## Explore the skills

<table>
<tr>
<td width="50%" valign="top">
<h3>01 · OpenAPI Compatibility Audit</h3>
<p><b>Catch likely API breaking changes before an SDK release.</b></p>
<p>Diff two local OpenAPI 3.x specs. Flags removed routes, newly required fields, narrowed input enums, missing successful responses and more. Explains every finding with a location and manual verification guidance.</p>
<p><a href="https://github.com/Kanompung1988/openapi-compat-audit"><b>Source, README & install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/openapi-compat-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/openapi-compat-audit/actions/workflows/ci.yml/badge.svg" alt="OpenAPI independent CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>02 · CI Log Triage</h3>
<p><b>From a failed build to evidence instead of guesses.</b></p>
<p>Analyze a local build/CI log, group TypeScript, dependency and assertion failures, and return line-referenced evidence plus safe next checks. Regex confidence hints are not claimed as root-cause certainty.</p>
<p><a href="https://github.com/Kanompung1988/ci-log-triage"><b>Source, README & install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/ci-log-triage/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/ci-log-triage/actions/workflows/ci.yml/badge.svg" alt="CI Triage independent CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>03 · GHA Trust Boundary Audit</h3>
<p><b>Line-level review of privileged GitHub Actions trust crossings.</b></p>
<p>Read-only inspection of pull_request_target checkout and execution, script interpolation from untrusted event values, token permissions and mutable actions. Includes conservative severity and remediation.</p>
<p><a href="https://github.com/Kanompung1988/gha-trust-boundary-audit"><b>Source, README & install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/gha-trust-boundary-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/gha-trust-boundary-audit/actions/workflows/ci.yml/badge.svg" alt="GHA Trust Boundary CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>04 · Env Contract Audit</h3>
<p><b>Find environment-variable documentation drift before deploy.</b></p>
<p>Offline names-only comparison of Python/Node/Vite references with .env.example; flags missing declarations and suspect public-bundle names without reading actual secrets.</p>
<p><a href="https://github.com/Kanompung1988/env-contract-audit"><b>Source, README & install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/env-contract-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/env-contract-audit/actions/workflows/ci.yml/badge.svg" alt="Env Contract CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>05 · PG Migration Risk Audit</h3>
<p><b>Find PostgreSQL migration lock and data-loss risks before deployment.</b></p>
<p>Offline, line-level review of SQL migrations for DROP, TRUNCATE, unbounded writes and concurrent index transaction issues. Reads files only; never executes SQL or connects to the database.</p>
<p><a href="https://github.com/Kanompung1988/pg-migration-risk-audit"><b>Source, README & install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/pg-migration-risk-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/pg-migration-risk-audit/actions/workflows/ci.yml/badge.svg" alt="PG Migration independent CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>06 · Docker Context Guard</h3>
<p><b>Review what Docker might send into a build context.</b></p>
<p>Read-only review of Dockerfile COPY/ADD, .dockerignore precedence, sensitive-looking filenames and ARG/ENV key names without reading secret values. The matcher is deliberately an approximation.</p>
<p><a href="https://github.com/Kanompung1988/docker-context-guard"><b>Source, README & install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/docker-context-guard/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/docker-context-guard/actions/workflows/ci.yml/badge.svg" alt="Docker Context independent CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>07 · Python Artifact Audit</h3>
<p><b>Review the archive you actually ship to PyPI.</b></p>
<p>Inspect built wheels and source archives offline for path traversal-looking entries, sensitive-looking filenames, duplicate members and selected metadata defects. Does not extract or execute packages or inspect secret values.</p>
<p><a href="https://github.com/Kanompung1988/python-artifact-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/python-artifact-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/python-artifact-audit/actions/workflows/ci.yml/badge.svg" alt="Python artifact audit CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>08 · Kubernetes RBAC Rights Audit</h3>
<p><b>Make least-privilege changes reviewable before deployment.</b></p>
<p>Inspect Role/ClusterRole and bindings as local YAML/JSON; flag wildcard access, secrets list, escalation verbs, cluster-admin grants and risky identity bindings, with evidence and namespace scope.</p>
<p><a href="https://github.com/Kanompung1988/k8s-rbac-rights-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/k8s-rbac-rights-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/k8s-rbac-rights-audit/actions/workflows/ci.yml/badge.svg" alt="Kubernetes RBAC audit CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>09 · Terraform Plan Impact Audit</h3>
<p><b>Turn a saved Terraform plan into a values-blind change-risk report.</b></p>
<p>Read local `terraform show -json` plans and flag deletes, replacement ordering, root-output removal and drift without printing secret values. Intended for review, never a substitute for a deployment approval.</p>
<p><a href="https://github.com/Kanompung1988/terraform-plan-impact-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/terraform-plan-impact-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/terraform-plan-impact-audit/actions/workflows/ci.yml/badge.svg" alt="Terraform Plan Impact Audit CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>10 · Kubernetes NetworkPolicy Scope Audit</h3>
<p><b>Explain who a NetworkPolicy selector may allow before applying YAML.</b></p>
<p>Offline, read-only inspection of namespace/pod selector scopes, broad peers, CIDRs and ports. Explains combined selector semantics, not the full effective behavior of a CNI.</p>
<p><a href="https://github.com/Kanompung1988/k8s-netpol-scope-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/k8s-netpol-scope-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/k8s-netpol-scope-audit/actions/workflows/ci.yml/badge.svg" alt="Kubernetes NetworkPolicy Scope Audit CI"></a></p>
</td>
</tr>

<tr>
<td width="50%" valign="top">
<h3>11 · CODEOWNERS Review Gap Audit</h3>
<p><b>Find ownership gaps before a critical file gets merged without intended reviewers.</b></p>
<p>Offline audit of documented CODEOWNERS pattern precedence, missing and ownerless matches for selected high-risk paths. Does not prove branch rules or actual reviewer permissions.</p>
<p><a href="https://github.com/Kanompung1988/codeowners-review-gap-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/codeowners-review-gap-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/codeowners-review-gap-audit/actions/workflows/ci.yml/badge.svg" alt="CODEOWNERS review-gap CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>12 · Kubernetes Image Pin Audit</h3>
<p><b>Review mutable image references and pull policies before deployment.</b></p>
<p>Offline inspection of Kubernetes YAML for tag/digest syntax and imagePullPolicy combinations. It does not connect to registries or verify actual image integrity.</p>
<p><a href="https://github.com/Kanompung1988/k8s-image-pin-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/k8s-image-pin-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/k8s-image-pin-audit/actions/workflows/ci.yml/badge.svg" alt="Kubernetes image pin CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>13 · Compose Port Exposure Audit</h3>
<p><b>Review published Docker Compose ports before opening host interfaces.</b></p>
<p>Offline, line-neutral service/port mapping review for default/all-interface binds, published data service ports, explicit loopback, host networking and unresolved interpolation. This is not a live port scan.</p>
<p><a href="https://github.com/Kanompung1988/compose-port-exposure-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/compose-port-exposure-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/compose-port-exposure-audit/actions/workflows/ci.yml/badge.svg" alt="Compose Port Exposure CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>14 · Helm Values Contract Audit</h3>
<p><b>Find Helm template references absent from local values.yaml defaults.</b></p>
<p>Conservative Go-template text scanner for literal .Values/index lookups. Missing defaults are review signals, not certain deployment failures; dynamic expressions are flagged.</p>
<p><a href="https://github.com/Kanompung1988/helm-values-contract-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/helm-values-contract-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/helm-values-contract-audit/actions/workflows/ci.yml/badge.svg" alt="Helm Values Contract CI"></a></p>
</td>
</tr>

<tr>
<td width="50%" valign="top">
<h3>15 · AWS GitHub OIDC Trust Audit</h3>
<p><b>Review which repository, branch and audience an AWS trust policy really accepts.</b></p>
<p>Offline, bounded IAM trust-policy JSON assessment of GitHub OIDC sub/aud claims and operators. Not a live IAM effective-permission evaluator.</p>
<p><a href="https://github.com/Kanompung1988/aws-github-oidc-trust-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/aws-github-oidc-trust-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/aws-github-oidc-trust-audit/actions/workflows/ci.yml/badge.svg" alt="AWS OIDC trust CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>16 · npm Export Map Audit</h3>
<p><b>Spot broken public Node.js package entrypoints before publishing.</b></p>
<p>Offline package.json exports target path, condition/subpath shape, encoding and optional built-file review. Not a complete Node.js resolver.</p>
<p><a href="https://github.com/Kanompung1988/npm-export-map-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/npm-export-map-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/npm-export-map-audit/actions/workflows/ci.yml/badge.svg" alt="npm export map CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>17 · Compose Startup Readiness Audit</h3>
<p><b>Stop mistaking a started container for a ready service.</b></p>
<p>Offline Compose depends_on, healthcheck and dependency-cycle review; no Docker daemon or multi-file merge simulation.</p>
<p><a href="https://github.com/Kanompung1988/compose-startup-readiness-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/compose-startup-readiness-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/compose-startup-readiness-audit/actions/workflows/ci.yml/badge.svg" alt="Compose startup readiness CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>18 · Python Entry-point Contract Audit</h3>
<p><b>Catch broken pyproject CLI command metadata before release.</b></p>
<p>Offline PEP 621 entrypoint reference and local Python target checks; no import execution or dynamic backend resolution.</p>
<p><a href="https://github.com/Kanompung1988/python-entrypoint-contract-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/python-entrypoint-contract-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/python-entrypoint-contract-audit/actions/workflows/ci.yml/badge.svg" alt="Python entry-point contract CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>19 · Kubernetes PDB Scope Audit</h3>
<p><b>Review pod disruption budget selectors before voluntary evictions.</b></p>
<p>Offline policy/v1 PDB checks for all-pod/null selectors, explicit Pod overlap and risky availability fields; no cluster API calls or eviction predictions.</p>
<p><a href="https://github.com/Kanompung1988/k8s-pdb-scope-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/workflows/ci.yml/badge.svg" alt="K8s PDB independent CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>20 · pip Index Boundary Audit</h3>
<p><b>Keep package-origin assumptions visible before pip install.</b></p>
<p>Read-only requirements file inspection for extra indexes, trusted hosts, HTTP transport and include-boundary escapes; credentials never echoed.</p>
<p><a href="https://github.com/Kanompung1988/pip-index-boundary-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/pip-index-boundary-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/pip-index-boundary-audit/actions/workflows/ci.yml/badge.svg" alt="pip Index independent CI"></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>21 · Python Dependency Group Audit</h3>
<p><b>Keep PEP 735 dependency-group declarations consistent without installing dependencies.</b></p>
<p>Offline review of normalized group-name collisions, invalid PEP 508 specifiers, malformed/missing include-group references and cycles. Produces stable rule IDs and JSON evidence, not dependency resolution.</p>
<p><a href="https://github.com/Kanompung1988/py-dependency-group-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/py-dependency-group-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/py-dependency-group-audit/actions/workflows/ci.yml/badge.svg" alt="Python dependency group audit independent CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>22 · PostgreSQL RLS Policy Audit</h3>
<p><b>Review row security DDL before a table is exposed to the wrong role.</b></p>
<p>Offline inspection of PostgreSQL ENABLE/DISABLE/FORCE RLS, CREATE POLICY, PUBLIC grants and literal-true policy predicates. Static source review, not an effective-permission check of a live database.</p>
<p><a href="https://github.com/Kanompung1988/pg-rls-policy-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/pg-rls-policy-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/pg-rls-policy-audit/actions/workflows/ci.yml/badge.svg" alt="PostgreSQL RLS policy audit independent CI"></a></p>
</td>
</tr>

<tr>
<td width="50%" valign="top">
<h3>23 · NGINX Header Inheritance Audit</h3>
<p><b>Prevent accidental security-header loss in nested NGINX blocks.</b></p>
<p>Offline, read-only check of add_header replacement/inheritance, add_header_inherit merge/off and missing always; includes are flagged as unresolved. No live NGINX inspection.</p>
<p><a href="https://github.com/Kanompung1988/nginx-header-inheritance-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/nginx-header-inheritance-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/nginx-header-inheritance-audit/actions/workflows/ci.yml/badge.svg" alt="NGINX header inheritance CI"></a></p>
</td>
<td width="50%" valign="top">
<h3>24 · npm Lifecycle Script Policy Audit</h3>
<p><b>Know which npm hooks may run during install, ci, pack and publish.</b></p>
<p>Offline package.json lifecycle-hook mapping and implicit binding.gyp detection without executing npm or showing script bodies; one supplied package at a time.</p>
<p><a href="https://github.com/Kanompung1988/npm-lifecycle-policy-audit"><b>Source, README &amp; install →</b></a></p>
<p><a href="https://github.com/Kanompung1988/npm-lifecycle-policy-audit/actions/workflows/ci.yml"><img src="https://github.com/Kanompung1988/npm-lifecycle-policy-audit/actions/workflows/ci.yml/badge.svg" alt="npm Lifecycle Policy CI"></a></p>
</td>
</tr>
</table>

| Skill | CLI | Verified QA evidence | Repository |
|---|---|---|---|
| OpenAPI audit | Local JSON/YAML OpenAPI 3.x comparison | [Python 3.10/3.12 — 16 unit tests + 1 smoke each](https://github.com/Kanompung1988/openapi-compat-audit/actions/runs/40093092063) | [openapi-compat-audit](https://github.com/Kanompung1988/openapi-compat-audit) |
| CI log triage | Local text CI log classification | [Python 3.10/3.12 — 16 unit tests + 1 smoke each](https://github.com/Kanompung1988/ci-log-triage/actions/runs/40093094810) | [ci-log-triage](https://github.com/Kanompung1988/ci-log-triage) |
| GHA trust boundary | Local GitHub Actions YAML static review | [Python 3.10/3.12 — 23 unit tests + CLI smoke each](https://github.com/Kanompung1988/gha-trust-boundary-audit/actions/runs/40258709081) | [gha-trust-boundary-audit](https://github.com/Kanompung1988/gha-trust-boundary-audit) |
| Env contract | Offline code/example env-key name comparison | [Python 3.10/3.12 — 25 unit tests + CLI smoke each](https://github.com/Kanompung1988/env-contract-audit/actions/runs/40258713283) | [env-contract-audit](https://github.com/Kanompung1988/env-contract-audit) |

| PostgreSQL migration risk | Offline SQL schema/data migration review | [Python 3.10/3.12 — 33 unit tests + fixture smoke each](https://github.com/Kanompung1988/pg-migration-risk-audit/actions/runs/40437637025) | [pg-migration-risk-audit](https://github.com/Kanompung1988/pg-migration-risk-audit) |
| Docker build context | Offline Dockerfile, .dockerignore and filenames review | [Python 3.10/3.12 — 26 unit tests + fixture smoke each](https://github.com/Kanompung1988/docker-context-guard/actions/runs/40437682390) | [docker-context-guard](https://github.com/Kanompung1988/docker-context-guard) |
| Python artifact archive audit | Offline wheel/sdist header, path and metadata review | [Python 3.10/3.12 — 27 tests + safe/unsafe fixture smoke each](https://github.com/Kanompung1988/python-artifact-audit/actions/runs/40620229042) | [python-artifact-audit](https://github.com/Kanompung1988/python-artifact-audit) |
| Kubernetes RBAC permissions audit | Offline namespaced/cluster-scope RBAC YAML/JSON review | [Python 3.10/3.12 — 33 tests + safe/unsafe fixture smoke each](https://github.com/Kanompung1988/k8s-rbac-rights-audit/actions/runs/40620234811) | [k8s-rbac-rights-audit](https://github.com/Kanompung1988/k8s-rbac-rights-audit) |
| Terraform saved-plan risk | Local values-blind JSON review | [Python 3.10/3.12 — 22 tests + safe/review fixture smoke each](https://github.com/Kanompung1988/terraform-plan-impact-audit/actions/runs/40805302365) | [terraform-plan-impact-audit](https://github.com/Kanompung1988/terraform-plan-impact-audit) |
| Kubernetes NetworkPolicy peer scope | Offline read-only selector semantics audit | [Python 3.10/3.12 — 26 tests + safe/review fixture smoke each](https://github.com/Kanompung1988/k8s-netpol-scope-audit/actions/runs/40805308144) | [k8s-netpol-scope-audit](https://github.com/Kanompung1988/k8s-netpol-scope-audit) |

| CODEOWNERS review gap | Offline selected critical-path owner matching and precedence review | [Python 3.10/3.12 — 30 tests + synthetic CLI smoke per version](https://github.com/Kanompung1988/codeowners-review-gap-audit/actions/runs/40992122453) | [codeowners-review-gap-audit](https://github.com/Kanompung1988/codeowners-review-gap-audit) |
| Kubernetes image pinning | Offline rendered manifest image tag/digest and pull-policy inspection | [Python 3.10/3.12 — 38 tests + synthetic CLI smoke per version](https://github.com/Kanompung1988/k8s-image-pin-audit/actions/runs/40992129587) | [k8s-image-pin-audit](https://github.com/Kanompung1988/k8s-image-pin-audit) |

| Compose port exposure | Read-only Compose YAML port and host-network heuristic | [Python 3.10/3.12 — 30 unit tests + safe/review fixture smoke each](https://github.com/Kanompung1988/compose-port-exposure-audit/actions/runs/41158191035) | [compose-port-exposure-audit](https://github.com/Kanompung1988/compose-port-exposure-audit) |
| Helm values contract | Literal Helm .Values/index paths vs. local defaults | [Python 3.10/3.12 — 30 unit tests + safe/review fixture smoke each](https://github.com/Kanompung1988/helm-values-contract-audit/actions/runs/41158196325) | [helm-values-contract-audit](https://github.com/Kanompung1988/helm-values-contract-audit) |
| AWS GitHub OIDC trust | Read-only IAM role trust-policy JSON subject/audience review | [Python 3.10/3.12 — 27 tests + synthetic fixture smoke each](https://github.com/Kanompung1988/aws-github-oidc-trust-audit/actions/runs/41263922125) | [aws-github-oidc-trust-audit](https://github.com/Kanompung1988/aws-github-oidc-trust-audit) |
| npm export map | Offline Node.js package.json exports target contract check | [Python 3.10/3.12 — 32 tests + synthetic fixture smoke each](https://github.com/Kanompung1988/npm-export-map-audit/actions/runs/41263928023) | [npm-export-map-audit](https://github.com/Kanompung1988/npm-export-map-audit) |

| Compose startup readiness | Offline service graph, healthcheck and depends_on contract review | [Python 3.10/3.12 — 26 tests + synthetic fixture smoke each](https://github.com/Kanompung1988/compose-startup-readiness-audit/actions/runs/41376691671) | [compose-startup-readiness-audit](https://github.com/Kanompung1988/compose-startup-readiness-audit) |
| Python entry-point contract | Offline pyproject CLI metadata and local module/attribute presence analysis | [Python 3.10/3.12 — 28 tests + synthetic fixture smoke each](https://github.com/Kanompung1988/python-entrypoint-contract-audit/actions/runs/41376699733) | [python-entrypoint-contract-audit](https://github.com/Kanompung1988/python-entrypoint-contract-audit) |

| Kubernetes PDB scope | Read-only policy/v1 selector and supplied Pod-overlap review | [Python 3.10/3.12 — 20 tests + fixtures](https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/runs/41566232466) | [k8s-pdb-scope-audit](https://github.com/Kanompung1988/k8s-pdb-scope-audit) |
| pip index boundary | Read-only requirements/index boundary, include and credential-safe diagnostics | [Python 3.10/3.12 — 20 tests + fixtures](https://github.com/Kanompung1988/pip-index-boundary-audit/actions/runs/41566240807) | [pip-index-boundary-audit](https://github.com/Kanompung1988/pip-index-boundary-audit) |
| Python dependency groups | Read-only PEP 735 group declarations, PEP 508 specifiers and include graph | [Python 3.10/3.12 — 28 tests + safe/review fixture smoke](https://github.com/Kanompung1988/py-dependency-group-audit/actions/runs/41759829260) | [py-dependency-group-audit](https://github.com/Kanompung1988/py-dependency-group-audit) |
| PostgreSQL RLS policy | Read-only RLS DDL intent and literal policy scope review | [Python 3.10/3.12 — 28 tests + safe/review fixture smoke](https://github.com/Kanompung1988/pg-rls-policy-audit/actions/runs/41759837243) | [pg-rls-policy-audit](https://github.com/Kanompung1988/pg-rls-policy-audit) |

| NGINX header inheritance | Read-only local NGINX add_header and add_header_inherit scope review | [Python 3.10/3.12 — 26 tests + safe/review fixture smoke](https://github.com/Kanompung1988/nginx-header-inheritance-audit/actions/runs/41952808524) | [nginx-header-inheritance-audit](https://github.com/Kanompung1988/nginx-header-inheritance-audit) |
| npm lifecycle script policy | Read-only package.json install/pack/publish hook contract review | [Python 3.10/3.12 — 27 tests + safe/review fixture smoke](https://github.com/Kanompung1988/npm-lifecycle-policy-audit/actions/runs/41952826099) | [npm-lifecycle-policy-audit](https://github.com/Kanompung1988/npm-lifecycle-policy-audit) |

## How to install

Each repository includes its own `SKILL.md`, standalone source code, license, examples and tests. Choose **one** from the table above, then clone it into your own project.

**Example — Claude Code (OpenAPI audit):**

```bash
mkdir -p .claude/skills
git clone --depth 1 https://github.com/Kanompung1988/openapi-compat-audit.git .claude/skills/openapi-compat-audit
```

**Example — Codex (CI log triage):**

```bash
mkdir -p .agents/skills
git clone --depth 1 https://github.com/Kanompung1988/ci-log-triage.git .agents/skills/ci-log-triage
```

Read the specific repository's README and [Agent Skills specification](https://agentskills.io/specification) before using the tool. Neither script makes network AI API calls; no key is needed for the included synthetic examples.

## How we work

```mermaid
flowchart LR
    A[Real developer pain point] --> B[8 ideas, scored and deduplicated]
    B --> C[Build up to 2 focused skills]
    C --> D[Python tests and real CLI fixture]
    D --> E[Independent public repository and PR]
    E --> F{CI green on both versions?}
    F -->|No| D
    F -->|Yes| G[Merge, verify PUBLIC main]
    G --> H[Add project link to this portfolio]
```

**Release gate:** Quality ≥85/100 is an internal editorial filter, not a claim of external adoption. A project ships only when tests pass, the source is public, and documentation is complete. No obligation to release a weak skill every day. **Skill Lab social publishing is OFF by owner instruction (2026-10-25)**, including Instagram and Facebook. Code releases continue normally; no marketing posts are queued by this workflow.

The technical runbook is [Skill Lab operations](docs/SKILL_LAB_OPERATIONS.md); verified episode history is [EPISODES.md](docs/EPISODES.md). Historic candidate research is [CANDIDATES-AND-SOURCES.md](CANDIDATES-AND-SOURCES.md); [EP.02's scored eight-candidate research](docs/CANDIDATE_RESEARCH_2026-10-26.md); [EP.03 research](docs/CANDIDATE_RESEARCH_2026-10-27.md); [EP.04 research](docs/CANDIDATE_RESEARCH_2026-10-28.md); [EP.05 research](docs/CANDIDATE_RESEARCH_2026-10-29.md); [EP.06 research](docs/CANDIDATE_RESEARCH_2026-10-30.md).

## Reproducible evidence, not vanity metrics

The two EP.01 standalones passed **16 unit checks and 1 deterministic CLI demo** on both Python 3.10 and 3.12; follow the exact per-repository CI links above. We do **not** claim external user results, independent security audit, or the official `skills-ref` validator. EP.02 adds GHA Trust Boundary Audit (23 tests) and Env Contract Audit (25 tests), each green on Python 3.10 and 3.12 in its own PR CI. EP.03 adds PG Migration Risk Audit (33 tests) and Docker Context Guard (26 tests), both independently green on Python 3.10 and 3.12 in their own PR CI. [EP.03's eight scored pain points and exact verification](docs/CANDIDATE_RESEARCH_2026-10-27.md). EP.04 adds Python Artifact Audit (27 tests) and Kubernetes RBAC Rights Audit (33 tests), both green on Python 3.10 and 3.12 in their own PR and main CI, and publicly available in dedicated repositories. [EP.04's eight screened problems and actual CI evidence](docs/CANDIDATE_RESEARCH_2026-10-28.md). These static checks are heuristics, not a professional security certification. Tests cover selected synthetic edge cases and cannot guarantee complete package safety or effective Kubernetes authorization. No official `skills-ref` validator or independent external security review was claimed for EP.04.

EP.05 adds Terraform Plan Impact Audit (22 tests) and Kubernetes NetworkPolicy Scope Audit (26 tests), both individually green on Python 3.10 and 3.12 in PR and public-main CI. These are read-only, bounded review aids, not security or availability guarantees. [EP.05's eight screened problems, rule boundaries and CI evidence](docs/CANDIDATE_RESEARCH_2026-10-29.md). Social distribution remains **OFF**.

EP.06 adds CODEOWNERS Review Gap Audit (30 tests) and Kubernetes Image Pin Audit (38 tests), each validated on Python 3.10 and 3.12 with successful separate PR and public-main CI. Both are offline review helpers with explicitly bounded matching, input, and registry-related limitations, not evidence of protection settings or container image integrity. [EP.06's eight screened problems, test evidence and release links](docs/CANDIDATE_RESEARCH_2026-10-30.md). **Skill Lab social remains OFF.**

EP.07 adds **Compose Port Exposure Audit** (30 tests) and **Helm Values Contract Audit** (30 tests), both with clean PR CI and independent post-merge public-main CI on Python 3.10 and 3.12. This episode uses deliberately bounded static heuristics with clearly labeled unresolved cases; no live network exposure or Helm deployment success is asserted. [Read the 8-candidate research and exact release evidence](docs/CANDIDATE_RESEARCH_2026-10-31.md). **Skill Lab social remains OFF.**

EP.08 adds **AWS GitHub OIDC Trust Audit** (27 tests) and **npm Export Map Audit** (32 tests), each with green Python 3.10 and 3.12 PR CI and independently green public-main CI. These tools are offline, purposely conservative static analyzers, not proof of AWS authorization security or Node runtime import success. The code was reviewed for OIDC wildcard actions and percent-encoded export separator edge cases and re-tested on the latest head. [See the eight-candidate research, scored decisions, exact GitHub CI and provenance](docs/CANDIDATE_RESEARCH_2026-11-01.md). **Skill Lab social distribution remains OFF.**

EP.09 adds **Compose Startup Readiness Audit** (26 local unit tests) and **Python Entry-point Contract Audit** (28 local unit tests); each released in its own public repository with Python 3.10 and 3.12 PR and post-merge main CI jobs passing. The analyzers deliberately avoid executing application code or querying live Docker; they are read-only static review aids and cannot guarantee deployment readiness or package installation success. [Read the eight scored candidates, sources and exact CI evidence](docs/CANDIDATE_RESEARCH_2026-11-02.md). **Skill Lab social remains OFF.**

EP.10 adds **Kubernetes PDB Scope Audit** and **pip Index Boundary Audit** (20 local unit tests each), independently green on Python 3.10 and 3.12 in PR and post-merge main CI. These are bounded offline review aids, not proof of live Kubernetes evictions or package index provenance. [Read the eight scored candidates and verified release evidence](docs/CANDIDATE_RESEARCH_2026-11-03.md). **Skill Lab social remains OFF.**

EP.11 adds **Python Dependency Group Audit** (28 unit tests) and **PostgreSQL RLS Policy Audit** (28 unit tests), both in separate PUBLIC repositories with Python 3.10 and 3.12 PR/main CI green. The tools inspect local manifests and SQL without executing input or contacting production; checks are deliberately bounded, and not third-party security attestations. [Read the eight scored candidates and reproducible release evidence](docs/CANDIDATE_RESEARCH_2026-11-04.md). **Skill Lab Instagram/Facebook distribution remains OFF.**

## Roadmap and collaboration

Contribute to a **specific skill repository** using its Issues or Pull Requests. Suggestions for new skills are welcome as [portfolio issues](https://github.com/Kanompung1988/agent-skills/issues), but implementation and tests belong in a separate repository when released. Explore the [episode catalog](docs/EPISODES.md) to see what shipped and why.

## Maintainers · licensing

Built in public by **AREAZERO Skill Lab** · [GitHub @Kanompung1988](https://github.com/Kanompung1988) · Thai social series: **ทำให้ AI เก่งขึ้นทุกวัน**. Source/docs under MIT unless a repository says otherwise; the exact Area Zero brand logos are excluded from the software license. See [BRAND.md](BRAND.md) and each skill's own license.

<p align="center"><sub>AREAZERO Skill Lab · Build useful tools. Test honestly. Publish independently.</sub></p>


EP.12 adds **NGINX Header Inheritance Audit** (26 unit tests) and **npm Lifecycle Script Policy Audit** (27 unit tests), each independently passing PR and post-merge main CI on Python 3.10 and 3.12. [View eight scored candidates, primary sources, PR/main CI and release provenance](docs/CANDIDATE_RESEARCH_2026-11-05.md). Both are bounded offline review tools, not full nginx/npm emulation or production security audits. **Skill Lab social remains OFF; Daily AI Scout unaffected.**
