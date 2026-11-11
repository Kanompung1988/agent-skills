# EP.18 — eight developer pain points evaluated (2026-11-11)

**Selection method:** utility (25), distinctiveness vs existing 34 Skills (20), Claude/Codex relevance (15), implementation feasibility (15), audience (10), reproducible demonstration (10), shareability (5). Scores are subjective editorial filters, not third-party results. Only >=85 and tested releases qualify.

| Developer problem | U/25 | D/20 | Agent/15 | Feasible/15 | Audience/10 | Demo/10 | Share/5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Kubernetes CronJob timezone & DST contracts | 25 | 18 | 14 | 14 | 10 | 9 | 4 | **94** | 94 — Release |
| Argo CD sync option conflict & destructive apply | 24 | 18 | 14 | 14 | 9 | 9 | 4 | **92** | 92 — Release |
| GitHub deployment environment protection drift | 23 | 16 | 13 | 11 | 10 | 7 | 3 | **83** | 83 — Defer |
| OpenTelemetry HTTP attribute migration | 22 | 15 | 13 | 11 | 9 | 7 | 4 | **81** | 81 — Defer |
| npm registry provenance signatures | 22 | 14 | 12 | 11 | 9 | 8 | 4 | **80** | 80 — Defer |
| Terraform moved/removed resource lifecycle | 20 | 14 | 12 | 11 | 9 | 9 | 3 | **78** | 78 — Defer |
| Helm values schema and override collisions | 20 | 11 | 12 | 13 | 9 | 8 | 3 | **76** | 76 — Reject near-duplicate |
| Dependabot GitHub Actions permission boundaries | 19 | 11 | 12 | 12 | 9 | 8 | 3 | **74** | 74 — Reject near-duplicate |

## Problem evidence and originality screen

### 1. Kubernetes CronJob timezone & DST contracts
Local controller timezone defaults; invalid TZ in schedule; daylight-saving shifts; short startingDeadlineSeconds; Replace/Forbid and history loss. Source: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/

**Score/decision:** 94/100, 94 — Release. 

### 2. Argo CD sync option conflict & destructive apply
Replace precedence over SSA, Force effects, Validate=false, Prune=false, and automated prune+allowEmpty can surprise GitOps owners. Source: https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/

**Score/decision:** 92/100, 92 — Release. 

### 3. GitHub deployment environment protection drift
Effective environment rules require trusted API access and repo settings; offline workflows alone cannot prove approval protection. Source: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments

**Score/decision:** 83/100, 83 — Defer. 

### 4. OpenTelemetry HTTP attribute migration
Old/new HTTP semantic conventions and http/dup transition affect dashboards; needs broader language instrumentation coverage. Source: https://opentelemetry.io/docs/specs/semconv/non-normative/http-migration/

**Score/decision:** 81/100, 81 — Defer. 

### 5. npm registry provenance signatures
Provenance attestation verification needs actual package downloads, registry integrity and npm CLI rather than an ungrounded static claim. Source: https://docs.npmjs.com/viewing-package-provenance/

**Score/decision:** 80/100, 80 — Defer. 

### 6. Terraform moved/removed resource lifecycle
State move/removal context requires safe plan artifacts and deeper HCL parsing; keep distinct from existing Terraform plan-impact skill. Source: https://developer.hashicorp.com/terraform/language/block/moved

**Score/decision:** 78/100, 78 — Defer. 

### 7. Helm values schema and override collisions
Overlaps the existing Helm Values Contract Audit; demand new reproducible value-add before building. Source: https://helm.sh/docs/helm/helm_upgrade/

**Score/decision:** 76/100, 76 — Reject near-duplicate. 

### 8. Dependabot GitHub Actions permission boundaries
Token and secret restrictions are important but partly overlap two existing GitHub Actions trust/permission skills. Source: https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions

**Score/decision:** 74/100, 74 — Reject near-duplicate. 

## Independently verified code-release evidence

### Kubernetes CronJob Timezone & Schedule Audit — 94/100
- Public repository: https://github.com/Kanompung1988/k8s-cronjob-timezone-audit
- PR merged: https://github.com/Kanompung1988/k8s-cronjob-timezone-audit/pull/1
- PR-head CI Python 3.10 and 3.12: https://github.com/Kanompung1988/k8s-cronjob-timezone-audit/actions/runs/42944098600 — SUCCESS
- Post-merge CI on public default `main`: https://github.com/Kanompung1988/k8s-cronjob-timezone-audit/actions/runs/42944255705 — SUCCESS
- `main` commit: `0a1aca372a276b6ae4c91d3a3cc7b3e55dee9daf`
- GitHub job logs: 25/25 Python unit tests on each version, plus safe fixture clean, review fixture detected, SKILL.md frontmatter smoke.
- Limitations: does not parse all cron grammar or predict DST firing, cluster controller timing or live jobs.

### Argo CD Sync Option Boundary Audit — 92/100
- Public repository: https://github.com/Kanompung1988/argocd-sync-option-audit
- PR merged: https://github.com/Kanompung1988/argocd-sync-option-audit/pull/1
- PR-head CI Python 3.10 and 3.12: https://github.com/Kanompung1988/argocd-sync-option-audit/actions/runs/42944177177 — SUCCESS
- Post-merge CI on public default `main`: https://github.com/Kanompung1988/argocd-sync-option-audit/actions/runs/42944262402 — SUCCESS
- `main` commit: `f146e02cff91fb45966bf93eec3a1b7edfcbc84c`
- GitHub job logs: 24/24 Python unit tests on each version, safe fixture clean, review fixture detected, SKILL.md frontmatter smoke.
- Limitations: does not run Argo CD, evaluate all resource overrides or verify cluster effective behavior.

### Provisioning and architecture
- Authorized provisioner PR: https://github.com/Kanompung1988/Bot_new_areazero/pull/5 (MERGED).
- Authorized creation GitHub Actions: https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/42943978816 — SUCCESS.
- Source staged on nondefault branch: https://github.com/Kanompung1988/agent-skills/tree/skill-lab/ep18-2026-11-11-cronjob-argocd/skills
- Each public Skill repository owns code, docs, tests, CI, and MIT software license. Portfolio `main` has links and research only.
- Official `skills-ref` validator: **NOT_RUN**. Frontmatter smoke passed in real CI; not a substitute for official validation.
- External review: **NOT_PERFORMED**. Passing CI does not certify security or runtime correctness.
- Social publishing: **OFF** (Instagram and Facebook). No scheduling, modifications, or posting. Daily AI Scout untouched.
