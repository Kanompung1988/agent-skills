# AREAZERO Skill Lab — EP.20 research and verified code-only release

**Date:** 2026-11-13 (Asia/Bangkok). **Skill Lab Instagram/Facebook: OFF indefinitely by owner override (2026-10-25).** Daily AI Scout unchanged.

## Methodology

Eight actionable developer pain points screened for distinctness from the 38 existing portfolio skills. Editorial weights: utility (25), originality/distinctness (20), Claude Code/Codex fit (15), implementation feasibility (15), potential audience (10), reproducible demonstration (10), shareability (5). Ratings are internal judgments, **not measured demand or independent assessments**. Only >=85 may be published, and only after verified tests/PR CI/public default-branch content.

| Candidate | Utility /25 | Distinct /20 | Agent /15 | Feasibility /15 | Audience /10 | Demo /10 | Share /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GitHub Actions `cache-mode` explicit write overrides on low-trust triggers | 25 | 20 | 15 | 15 | 10 | 9 | 1 | **95** | **SHIPPED** `gha-cache-mode-boundary-audit` |
| StatefulSet `persistentVolumeClaimRetentionPolicy` Delete vs Retain surprises | 24 | 19 | 15 | 15 | 9 | 9 | 2 | **93** | **SHIPPED** `k8s-statefulset-pvc-audit` |
| npm trusted-publisher provenance/registry mismatch | 22 | 16 | 13 | 10 | 9 | 8 | 2 | 80 | Hold: authentic registry provenance requires online verification |
| OpenTelemetry HTTP semantic-convention cross-version drift | 22 | 14 | 13 | 11 | 9 | 8 | 2 | 79 | Hold: SDK/version-dependent convention complexity |
| Python editable-install vs wheel parity | 22 | 15 | 12 | 12 | 8 | 7 | 2 | 78 | Hold: environment-dependent build parity and prior Python artifact coverage |
| Docker Buildx SBOM/attestation metadata consistency | 20 | 12 | 13 | 12 | 9 | 9 | 2 | 77 | Hold: strong overlap with prior artifact/BuildKit audit skills |
| Dependabot-triggered workflow secret restrictions | 20 | 12 | 13 | 13 | 9 | 7 | 1 | 75 | Hold: overlaps GitHub Actions trust tools |
| Argo Rollouts analysis-run threshold drift | 20 | 13 | 13 | 11 | 8 | 8 | 1 | 74 | Hold: controller-specific integration and no robust fixture coverage |

## Primary-source references and boundaries

- [GitHub cache-mode released on 2026-09-10](https://github.blog/changelog/2026-09-10-control-github-actions-cache-access-with-cache-mode/): explicit cache write controls and secure read-only defaults. Job-level cache-mode overrides workflow-level mode. Untrusted-trigger write override can reinstate poisoning risk.
- [GitHub read-only cache for low-trust events, 2026-06-26](https://github.blog/changelog/2026-06-26-read-only-actions-cache-for-untrusted-triggers/): trigger-based enforcement. Do not flag omitted cache-mode as insecure by default.
- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax): four accepted cache modes.
- [Kubernetes StatefulSet storage lifecycle](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/): `persistentVolumeClaimRetentionPolicy` stable since v1.32; omitted policies default Retain; Delete affects generated PVCs after deletion/scale-down.
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/): PersistentVolume reclaim behavior is separate and not inferred.
- [npm trusted publishers](https://docs.npmjs.com/trusted-publishers/) and [npm provenance](https://docs.npmjs.com/generating-provenance-statements/) for non-selected alternative.
- [PEP 660](https://peps.python.org/pep-0660/) for non-selected editable-install alternative.

## Verified independent GitHub release evidence

| Gate | GitHub cache-mode boundary audit | StatefulSet PVC retention audit |
|---|---|---|
| Independent public repo | [gha-cache-mode-boundary-audit](https://github.com/Kanompung1988/gha-cache-mode-boundary-audit) | [k8s-statefulset-pvc-audit](https://github.com/Kanompung1988/k8s-statefulset-pvc-audit) |
| Pull request | [#1 merged](https://github.com/Kanompung1988/gha-cache-mode-boundary-audit/pull/1) | [#1 merged](https://github.com/Kanompung1988/k8s-statefulset-pvc-audit/pull/1) |
| Public default branch | `main` at `80cfd9bc05c084895d7ee46da2d70941d6794528` | `main` at `dda3e661ba8dd730d4c4cb8935f19ff174be596e` |
| Successful PR CI | [43350088167](https://github.com/Kanompung1988/gha-cache-mode-boundary-audit/actions/runs/43350088167) | [43350288682](https://github.com/Kanompung1988/k8s-statefulset-pvc-audit/actions/runs/43350288682) |
| Successful post-merge main CI | [43350410352](https://github.com/Kanompung1988/gha-cache-mode-boundary-audit/actions/runs/43350410352) | [43350416986](https://github.com/Kanompung1988/k8s-statefulset-pvc-audit/actions/runs/43350416986) |
| Tests per Python version | 20/20 on Python 3.10 and 3.12 | 24/24 on Python 3.10 and 3.12 |
| CLI safe/review and metadata smoke | PASS | PASS |

**Provisioning:** [Bot_new_areazero PR #7 merged](https://github.com/Kanompung1988/Bot_new_areazero/pull/7); [authorized idempotent provisioning Actions run 43349872729 SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/43349872729). Existing 12 request records retained, two new requests appended. Complete packages staged on portfolio nondefault branch `skill-lab/ep20-2026-11-13-pvc-cache`; no skill source on portfolio main.

**Failure and correction:** The StatefulSet PR's first CI [run 43350140028](https://github.com/Kanompung1988/k8s-statefulset-pvc-audit/actions/runs/43350140028) failed 1/24 tests per version because PyYAML BaseLoader represents an empty document as an empty string rather than None. Corrected in the code and in the staging branch, reran CI to pass 24/24 on both Python versions, then merged.

**Quality limitations:** real CI tests and fixture smoke verified; official `skills-ref` validator **NOT_RUN**; local tests outside GitHub runner **NOT_RUN**; independent security review **NOT_DONE**; production runtime test **NOT_DONE**. The cache auditor does not prove cache-token privilege boundaries or analyze shell data flow. The PVC auditor does not inspect live clusters, PV reclaim modes, or backups. Original AREAZERO logo is kept separate from the MIT-licensed code.

**Publishing status:** GitHub code released. Skill Lab Instagram and Facebook **OFF**: no scheduling, Metricool/social write, reactivation, or social workflow change. Daily AI Scout untouched.
