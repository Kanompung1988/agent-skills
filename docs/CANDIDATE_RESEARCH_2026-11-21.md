# AREAZERO Skill Lab — EP.28 Research
Date: 2026-11-21

## Scoring rubric (100 points)
- Practical developer impact: 30
- Originality versus the existing AREAZERO portfolio: 25
- Fit for an agent-invoked workflow: 15
- Feasibility of safe, deterministic implementation: 15
- Testability and reproducible evidence: 10
- Likely adoption across teams: 5

Scores are internal prioritization judgments, not user-survey measurements. A score of 85 is a selection threshold, not proof of demand. We selected only the top two candidates and required real unit/fixture tests plus CI.

| # | Concrete pain point | Impact /30 | Originality /25 | Agent fit /15 | Feasibility /15 | Evidence /10 | Adoption /5 | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | RuntimeClass selector merge conflicts and Pod overhead shape/quantity drift | 29 | 24 | 14 | 14 | 9 | 4 | **94** | Build |
| 2 | Job/CronJob podFailurePolicy, indexed backoff, FailIndex and restartPolicy incompatibilities | 29 | 23 | 14 | 14 | 9 | 3 | **92** | Build |
| 3 | Docker Compose file-backed secret permission expectations and service grants | 27 | 22 | 13 | 14 | 9 | 4 | 89 | Defer |
| 4 | Deployment rolling-update availability/surge percentage rounding and stalled rollout budgets | 27 | 20 | 13 | 14 | 9 | 4 | 87 | Defer |
| 5 | workflow_run artifact hand-off from untrusted workflows into privileged contexts | 26 | 17 | 13 | 14 | 9 | 3 | 82 | Reject: overlaps existing GHA trust-boundary skills |
| 6 | Environment deployment branch/tag filter mismatches and wildcard assumptions | 25 | 16 | 13 | 14 | 9 | 4 | 81 | Reject: overlaps existing environment-gate skills |
| 7 | PEP 735 dependency-group include graph and cycles across project tooling | 24 | 15 | 13 | 14 | 9 | 4 | 79 | Reject: overlaps existing Python dependency-group coverage |
| 8 | Job activeDeadlineSeconds precedence, TTL cleanup and CronJob history retention | 24 | 15 | 12 | 13 | 9 | 5 | 78 | Defer: adjacent to selected Job failure-policy scope |

## Selected skills and evidence

### 1. k8s-runtimeclass-contract-audit — 94/100
Pain: a RuntimeClass can add scheduling constraints to a Pod. If a RuntimeClass and Pod set the same nodeSelector key to different values, the merged selector cannot be satisfied and admission rejects the Pod. RuntimeClass tolerations are appended to Pod tolerations; Pod overhead is also part of the scheduling/resource contract.

Implementation is deliberately offline: parse supplied YAML with safe_load_all, collect RuntimeClass objects, inspect Pod/workload templates, detect conflicting selector keys, validate handler/scheduling field shapes, and conservatively validate non-negative podFixed quantity syntax. An unresolved class reference is INFO, not an assertion that the cluster lacks it.

Tests: 24 unit tests, safe and review fixtures, package/frontmatter/logo integrity check. Local safe fixture exit 0; review fixture exit 2. GitHub Actions validates Python 3.10 and 3.12 and runs the official skills-ref validator.

### 2. k8s-job-failure-policy-audit — 92/100
Pain: Job failure behavior is governed by interacting fields. podFailurePolicy requires restartPolicy Never; rule order is significant; containerName must refer to a container or initContainer; FailIndex depends on per-index backoff; backoffLimitPerIndex requires Indexed completion and Never; and omitting backoffLimit when per-index backoff is configured changes the default from 6 to 2147483647.

Implementation is offline and read-only: inspect Job and CronJob jobTemplate specs, validate the listed policy/retry constraints, report the special default as INFO, and never run workloads or contact a cluster.

Tests: 26 unit tests, safe and review fixtures, package/frontmatter/logo integrity check. Local safe fixture exit 0; review fixture exit 2. GitHub Actions validates Python 3.10 and 3.12 and runs the official skills-ref validator.

## Deferred candidates — primary references
3. Compose secret grants and file-backed secret behavior: https://docs.docker.com/reference/compose-file/services/#secrets
4. Deployment rolling-update behavior: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment
5. workflow_run security boundary: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run
6. Deployment branch/tag rules: https://docs.github.com/en/actions/reference/deployments-and-environments#deployment-branches-and-tags
7. PEP 735 dependency groups: https://packaging.python.org/en/latest/specifications/dependency-groups/
8. Job deadline and TTL cleanup: https://kubernetes.io/docs/concepts/workloads/controllers/job/ and https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/

## Official technical references
- RuntimeClass: https://kubernetes.io/docs/concepts/containers/runtime-class/
- Pod overhead: https://kubernetes.io/docs/concepts/scheduling-eviction/pod-overhead/
- Job / Pod failure policy / indexed backoff: https://kubernetes.io/docs/concepts/workloads/controllers/job/
- Agent Skills specification: https://agentskills.io/specification
- Reference validator source: https://github.com/agentskills/agentskills/tree/main/skills-ref

## Scope and limitations
These tools analyze only the YAML supplied by the user. They do not query a cluster, validate against a specific API-server version, inspect installed runtime handlers/nodes, simulate controllers, or prove application retry idempotency. A clean static result is not production certification. The official skills-ref validator is run in GitHub CI; a local attempt to install it was blocked because the execution container cannot resolve github.com.


## Independently verified public release evidence

| Skill | PR | Default branch / commit | Post-merge CI |
|---|---|---|---|
| [k8s-runtimeclass-contract-audit](https://github.com/Kanompung1988/k8s-runtimeclass-contract-audit) | [PR #1 merged](https://github.com/Kanompung1988/k8s-runtimeclass-contract-audit/pull/1) | `main` · `77507bcc0561a685db2ba13c2554f0c0f30ac75d` | [Run 44855075655 — success](https://github.com/Kanompung1988/k8s-runtimeclass-contract-audit/actions/runs/44855075655) |
| [k8s-job-failure-policy-audit](https://github.com/Kanompung1988/k8s-job-failure-policy-audit) | [PR #1 merged](https://github.com/Kanompung1988/k8s-job-failure-policy-audit/pull/1) | `main` · `58d68f2834849bb59b714c5a6adc427a722661f7` | [Run 44855080977 — success](https://github.com/Kanompung1988/k8s-job-failure-policy-audit/actions/runs/44855080977) |

Both repositories were independently read back from GitHub after merge. The default branch is `main`, each root `SKILL.md` is present, repository visibility is Public, and the linked post-merge push workflow completed successfully. The workflow ran unit tests and safe/review CLI fixtures on Python 3.10 and 3.12. The official `skills-ref validate` step ran on Python 3.12 only because the upstream validator requires Python 3.11 or newer; the 3.10 leg still runs all project tests and fixtures.

The portfolio remains an index: source code is not merged into the portfolio default branch. The staging branch contains the package sources solely for the authorized provisioning/review workflow.
