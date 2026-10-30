# AREAZERO Skill Lab EP.06 — eight screened developer problems (2026-10-30)

**Editorial date:** 30 October 2026, Asia/Bangkok. **Series:** Make AI more useful every day. **Public releases:** up to two, only score >=85/100 and independently testable. Scores reflect internal engineering judgment, not measured industry demand, popularity, or external expert certification. No new vulnerability/incident is implied.

## Dedupe and method

Read the current public `agent-skills` portfolio, EP.01–EP.05 catalog and operations contract before selection. The existing ten skills cover OpenAPI compatibility, CI log triage, GitHub Actions trust boundaries, environment key drift, PostgreSQL migrations, Docker build context, Python distribution artifacts, Kubernetes RBAC, Terraform plan impact and Kubernetes NetworkPolicy selector scope. No candidate below reproduces one of those tools. Each research candidate has a primary documentation reference; separate operational feasibility from verified test coverage. Score breakdown: utility /25, originality and scope differentiation /20, Claude Code/Codex fit /15, feasible and safe offline implementation /15, audience /10, demonstrable tests /10, communication value /5.

| Practical developer problem | Utility /25 | Distinct /20 | Agent fit /15 | Feasibility /15 | Audience /10 | Tests /10 | Story /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Last-match CODEOWNERS patterns accidentally leave important workflows, infra, dependency locks or CODEOWNERS itself without owners; location precedence and parser errors go unnoticed | 24 | 18 | 15 | 14 | 9 | 10 | 4 | **94** | **BUILD** `codeowners-review-gap-audit`; names-only, intentionally bounded matching subset; see [GitHub CODEOWNERS docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners). |
| Mutable Kubernetes image tags and sticky `imagePullPolicy` defaults undermine rollout reproducibility; reviewer confuses a registry port with an image tag | 24 | 18 | 15 | 13 | 9 | 10 | 4 | **93** | **BUILD** `k8s-image-pin-audit`; static rendered YAML, not registry authentication; see [Kubernetes Images](https://kubernetes.io/docs/concepts/containers/images/). |
| Artifact attestation downloaded in CI but identity or trusted root not verified | 21 | 16 | 13 | 9 | 9 | 8 | 4 | **80** | DEFER: safe verification requires a trustworthy Sigstore/CLI integration rather than a simplistic JSON checker; see [GitHub offline verification](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline). |
| Docker Compose `depends_on` starts an unhealthy database and the app fails at boot, with complex healthcheck semantics | 22 | 14 | 13 | 11 | 8 | 9 | 4 | **81** | DEFER: behavioral claims depend on service health probes and runtime; see [Docker Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/). |
| Git submodule unexpectedly points at an out-of-policy commit or mismatches the intended upstream | 22 | 13 | 13 | 12 | 8 | 9 | 4 | **81** | DEFER: needs authenticated remote provenance and intentional update policy, not generic regex; see [Git submodule manual](https://git-scm.com/docs/git-submodule). |
| Deployment workflow references an environment without the intended approval or branch restrictions | 22 | 15 | 13 | 10 | 9 | 9 | 3 | **81** | DEFER: repository settings cannot be inferred from a workflow file alone; see [GitHub deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments). |
| npm dependency install lifecycle scripts run in unexpected CI contexts or violate scripted approval policy | 22 | 14 | 14 | 10 | 9 | 8 | 4 | **81** | DEFER: lifecycle defaults, npm version and workspace behavior require exact npm CLI compatibility; see [npm install scripts](https://docs.npmjs.com/cli/v11/commands/npm-install-scripts/). |
| OpenTelemetry semantic attribute migration breaks downstream dashboards without version-aware schema diffs | 21 | 15 | 13 | 10 | 8 | 8 | 3 | **78** | DEFER: broad regex would misstate a versioned semantic migration; see [OpenTelemetry convention migration](https://opentelemetry.io/docs/specs/semconv/non-normative/code-attrs-migration/). |

## Released skills and evidence

### Codeowners Review Gap Audit — 94/100 (internal editorial rating)
- Public standalone repository: https://github.com/Kanompung1988/codeowners-review-gap-audit
- Merged PR: https://github.com/Kanompung1988/codeowners-review-gap-audit/pull/1
- Public default-branch SHA: `4ba6f99819f8623437deb03f557788fddcc40d4b`.
- GitHub Actions on `main`: https://github.com/Kanompung1988/codeowners-review-gap-audit/actions/runs/40992122453 — Python 3.10 and 3.12 **SUCCESS**. Local Python 3.13: **30 unittest cases passed**, and CLI synthetic safe/review examples checked.
- Findings are limited to selected *tracked* critical paths. The Codeowners pattern matcher handles a documented subset; GitHub's actual code owner assignment, owner permissions, branch rulesets and GitHub's own parser remain authoritative. Do not interpret zero findings as enforcement proof.

### Kubernetes Image Pin Audit — 93/100 (internal editorial rating)
- Public standalone repository: https://github.com/Kanompung1988/k8s-image-pin-audit
- Merged PR: https://github.com/Kanompung1988/k8s-image-pin-audit/pull/1
- Public default-branch SHA: `5684e11b6887c216ead50a1d2aae81e827d9df87`.
- GitHub Actions on `main`: https://github.com/Kanompung1988/k8s-image-pin-audit/actions/runs/40992129587 — Python 3.10 and 3.12 **SUCCESS**. Local Python 3.13: **38 unittest cases passed**, including malformed CronJob/pull policy input regression tests and CLI synthetic examples.
- Does not verify that a registry digest exists, signature/provenance, tag immutability guarantees, admission controller mutation or observed node cache. An input that resembles a digest is not evidence of trusted bytes.

### Release process
- Stage ref `agent-skills/skill-lab/ep06-2026-10-30-staging` (non-default only); does not contain the public release on portfolio `main`.
- Public repo provisioning triggered by manifest update `Bot_new_areazero/main` commit `5d5e5afb4f3b4c795d9686c0be18c53803950298`. Verified [provisioner run SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/40991687770).
- Both projects have independent SKILL.md, script, fixtures, tests, references, CI and MIT code license; original logo included as exact unmodified blob SHA `e1d2a0686010b251a530f9ad7eaf9afddf6a706b`, excluded from MIT.
- PR CI and subsequent default-branch CI passed independently for each project on both listed Python versions. Local sample inputs are synthetic, not evidence of finding a real production vulnerability.
- Official `skills-ref` validation: **NOT_RUN**. Third-party independent/security review: **NOT_RUN**. An internal read-through and input-hardening regression review is **not** an independent review.

**Social distribution: OFF.** Under owner override dated 2026-10-25, no Skill Lab Instagram/Facebook posting, scheduling, rescheduling, or API writes occurred in this episode. Daily AI Scout is separate and unchanged.
