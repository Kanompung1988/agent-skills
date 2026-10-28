# EP.04 developer pain-point research — 2026-10-28

**Editorial date:** 28 October 2026, Asia/Bangkok. These are **engineering pain points** supported by upstream technical documentation, **not** claims that features or vulnerabilities were newly announced today. Dates of current product releases are not inferred. Reviewed previous six AREAZERO standalone tools (OpenAPI compatibility, CI logs, GitHub Actions trust boundaries, environment contract, PG migrations, Docker build contexts) to avoid repackaging them.

**Research method:** screen eight concrete problems against primary technical documentation; rate utility (25), distinctiveness relative to AREAZERO's previous six skills (20), usability as an autonomous Claude Code/Codex procedure (15), build feasibility and safety (15), developer audience (10), test/demo reproducibility (10), and communication clarity (5). All totals are **subjective internal editorial scores**, not benchmark or user-adoption results. Minimum selection threshold 85/100 and up to two released skills. Documentation links establish technical semantics only; they do not establish demand size, superiority or uniqueness across the whole ecosystem.

| Developer pain point | Utility /25 | Distinct /20 | Agent fit /15 | Feasible /15 | Audience /10 | Demo/tests /10 | Clarity /5 | Total | Decision | Primary technical reference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Python wheel/sdist release unexpectedly bundles sensitive-looking filenames, unsafe member paths, or lacks required archive metadata | 24 | 18 | 15 | 15 | 9 | 10 | 5 | **96** | **SELECT** — `python-artifact-audit` | [PyPA wheel format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/), [sdist specification](https://packaging.python.org/en/latest/specifications/source-distribution-format/) |
| Kubernetes RBAC YAML accidentally grants wildcard, secrets list, bind/escalate, pod exec, or overly broad identity permissions | 24 | 18 | 15 | 14 | 9 | 10 | 5 | **95** | **SELECT** — `k8s-rbac-rights-audit` | [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/), [RBAC reference](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) |
| CI artifacts lack verifiable supply-chain provenance, or provenance isn't verified before consumption | 22 | 15 | 14 | 10 | 9 | 8 | 4 | **82** | DEFER — trust roots and signed bundle verification require runtime and a distinct bounded design | [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations), [offline verification](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline) |
| Webhook handlers skip signature checks or use timing-sensitive equality on request bodies | 22 | 15 | 14 | 11 | 9 | 8 | 4 | **83** | DEFER — broad-framework static detection can miss proxy transformations and real request-body semantics | [GitHub validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) |
| Kubernetes NetworkPolicy YAML misinterprets empty selectors and combined namespace/pod selectors | 22 | 14 | 14 | 10 | 9 | 8 | 4 | **81** | DEFER — effective traffic behavior depends on networking plugin and other policies | [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) |
| Kubernetes workload images rely on mutable tags instead of stable digest references | 22 | 14 | 14 | 11 | 9 | 8 | 4 | **82** | DEFER — straightforward static lint lacks differentiation; some update workflows intentionally use tags | [Kubernetes images](https://kubernetes.io/docs/concepts/containers/images/) |
| npm CI dependency lockfile does not match manifest and produces non-reproducible install | 21 | 10 | 14 | 12 | 9 | 9 | 3 | **78** | DEFER — duplicates previous EP.03 screening; npm ci already rejects mismatches | [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/) |
| Docker build secrets are passed through ARG/ENV rather than dedicated BuildKit secret mounts | 21 | 9 | 13 | 11 | 9 | 7 | 4 | **74** | DEFER — overlaps existing Docker Context Guard; not sufficiently distinct this day | [Docker build secrets](https://docs.docker.com/build/building/secrets/) |

## Selection and safety boundaries

### Python Artifact Audit — internal editorial score 96/100

A **bounded, read-only, artifact-first** quality gate for the *actual archives intended to ship*. Wheel metadata convention requires `METADATA`, `WHEEL`, `RECORD`; modern sdists use a single `name-version` archive directory and `PKG-INFO`/`pyproject.toml`. The scanner lists ZIP/tar member *names and headers only*, without extracting, importing or executing packages. Rules PA001–PA007 flag path anomalies, filename patterns, duplicates and selected metadata defects. It does **not** inspect data contents, validate RECORD hashes, signatures, malware, dependencies or correct sdist name/version/metadata values. This is a release-review helper, not a security certification.

- Repository (public): https://github.com/Kanompung1988/python-artifact-audit
- PR #1 (merged): https://github.com/Kanompung1988/python-artifact-audit/pull/1
- PR head commit: `f0086c6a79e00491c9a9be112195421b3bd0f9f6`; merge/default-branch commit `b3577505a2c462a4fb0e9eb4febc55d912ea2553`.
- PR CI (verified): https://github.com/Kanompung1988/python-artifact-audit/actions/runs/40620105343
- Latest main CI (verified): https://github.com/Kanompung1988/python-artifact-audit/actions/runs/40620229042
- Jobs **Python 3.10 and Python 3.12 SUCCESS**, confirmed workflow step reports **27 unit tests** and deterministic safe/unsafe fixture checks. One latest main job log personally re-read and contains `Ran 27 tests` followed by `OK`. Both job statuses independently checked.
- Root `SKILL.md`, `README.md`, self-contained `scripts/audit.py`, tests, examples, references, license, hero SVG and CI file fetched from PUBLIC `main`.

### Kubernetes RBAC Rights Audit — internal editorial score 95/100

An **offline YAML/JSON manifest review** for Role, ClusterRole, RoleBinding and ClusterRoleBinding, covering wildcard resources/verbs, Secret reads (including list/watch), escalation/bind/impersonation, workload creation, exec, cluster-admin and risky service-account/group bindings. The scanner differentiates RoleBinding namespace scope from ClusterRoleBinding cluster scope, uses a bounded safe YAML loader and emits policy-field evidence. It does **not** call a cluster, resolve full aggregation/admission/nested controllers, or prove exploitability. False positive/negative cases remain possible.

- Repository (public): https://github.com/Kanompung1988/k8s-rbac-rights-audit
- PR #1 (merged): https://github.com/Kanompung1988/k8s-rbac-rights-audit/pull/1
- PR head commit: `7917327a7d8e71a050923096e6d87c60c5490e89`; merge/default-branch commit `a3f357533be122e41adb328c3efb79082c44caa5`.
- PR CI (verified): https://github.com/Kanompung1988/k8s-rbac-rights-audit/actions/runs/40620109117
- Latest main CI (verified): https://github.com/Kanompung1988/k8s-rbac-rights-audit/actions/runs/40620234811
- Jobs **Python 3.10 and Python 3.12 SUCCESS**, confirmed workflow step reports **33 unit tests** and safe/unsafe synthetic-manifest CLI smoke. One latest main job log personally re-read and contains `Ran 33 tests` followed by `OK`. Both job statuses independently checked.
- Root `SKILL.md`, `README.md`, `scripts/audit.py`, pinned PyYAML requirement, tests, fixtures, references, license, hero SVG and CI file fetched from PUBLIC `main`.

## Release standard and honest limits

Both code projects were created via the approved `Bot_new_areazero` Actions repository provisioner, with successful [provisioner run 40619869809](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/40619869809); staged source remained on `agent-skills` nondefault `skill-lab/ep04-2026-10-28-staging` branch. The provisioner's success alone is **not** the release gate. Each stand-alone repository has since separately completed a feature-branch PR and its own passing CI on both supported Python versions, merged and fetched from public `main`.

**Independent external human security review:** NOT RUN. **Official agentskills `skills-ref` validator:** NOT RUN (not claimed). **Direct local re-execution by this reporting step:** NOT RUN; rely on verified public GitHub runner logs from 2026-10-28. Tests are synthetic scoped checks, not evidence of production adoption or assurance of vulnerability-free code.

**Social:** **OFF** — owner override dated 2026-10-25 remains effective. No Skill Lab Instagram/Facebook posting, scheduling, or enabling may be inferred from this release; Daily AI Scout is a separate series. This record is for GitHub code discovery, not social media.
