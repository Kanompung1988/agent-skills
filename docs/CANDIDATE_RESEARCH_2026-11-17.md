# AREAZERO Skill Lab — EP.24 developer pain points and verified independent releases

**Date:** 2026-11-17 (Asia/Bangkok). **GitHub code: PUBLISHED in two separate public repositories.** **Skill Lab social:** OFF indefinitely; no Instagram @areazero.ai / Facebook AreaZero scheduling or posting. **Daily AI Scout:** untouched.

## Research: eight concrete developer pain points

Editorial scoring rubric: usefulness /25, distinctiveness from existing 46-Skill portfolio /20, Claude Code / Codex applicability /15, bounded engineering feasibility /15, audience /10, reproducible validation /10, communication /5. Each score is an **internal judgment, not user-demand analytics or security certification**. Release gate: score >=85, genuinely separate functionality, source in independent public repository, passing real CI on latest PR head and public default branch.

| Developer pain point | Utility /25 | Distinct /20 | Agent /15 | Feasible /15 | Audience /10 | Demo /10 | Share /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CSI VolumeSnapshotClass default/deletion, VolumeSnapshotContent binding and restore mode errors before Kubernetes backups | 24 | 18 | 14 | 14 | 9 | 10 | 4 | **93** | **RELEASE** — bounded manifest review, 24 tests each Python version |
| Python PEP 660 editable-wheel metadata differs from regular wheels or hides unexpected editable-only dependencies | 23 | 18 | 14 | 14 | 8 | 10 | 4 | **91** | **RELEASE** — local wheel metadata, 16 tests each Python version |
| Renovate lockfile maintenance schedules conflict with routine dependency PRs | 20 | 15 | 12 | 12 | 8 | 9 | 4 | 80 | DEFER — manager-specific schedule semantics difficult to emulate reliably |
| Sigstore/cosign certificate identity or issuer verification boundaries | 20 | 14 | 12 | 12 | 8 | 9 | 4 | 79 | DEFER — requires real cryptographic verification, overlaps existing attestations |
| Gateway API controller status observedGeneration freshness on route conditions | 20 | 14 | 12 | 12 | 8 | 8 | 4 | 78 | DEFER — needs live controller observations, adjacent to earlier ReferenceGrant skill |
| Self-hosted GitHub Actions runner group and label mismatch | 20 | 13 | 13 | 12 | 8 | 8 | 3 | 77 | DEFER — accurate group inventory and runner eligibility require API access |
| Helm OCI chart provenance verification and identity | 19 | 14 | 12 | 12 | 8 | 8 | 3 | 76 | DEFER — real keyring/signature verification is essential; older Helm lock skill is unrelated |
| Argo Rollouts templated Analysis arguments diverge from rollout specifications | 19 | 13 | 12 | 12 | 8 | 8 | 3 | 75 | REJECT — partly overlaps existing Argo Rollouts Analysis Audit |

**Why the selected two differ from prior work:** The new CSI snapshot reviewer covers snapshot class retention, snapshot content and restore-mode references rather than previous StatefulSet PVC retention or topology scheduling. PEP 660 wheel comparison covers editable install *distribution metadata* rather than the previous Python CLI entry-point or dependency group audits. Both can be run against explicit synthetic inputs without production credentials or side effects. Their novelty scores represent an internal assessment only.

## Source specifications and primary documentation

1. [Agent Skills specification](https://agentskills.io/specification)
2. [Kubernetes Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
3. [Kubernetes VolumeSnapshotClasses](https://kubernetes.io/docs/concepts/storage/volume-snapshot-classes/)
4. [PEP 660 Editable Installs](https://peps.python.org/pep-0660/)
5. [Python core distribution metadata](https://packaging.python.org/en/latest/specifications/core-metadata/)
6. [Renovate lockFileMaintenance](https://docs.renovatebot.com/configuration-options/#lockfilemaintenance)
7. [Sigstore cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/)
8. [Gateway API specification](https://gateway-api.sigs.k8s.io/reference/spec/)
9. [GitHub Actions self-hosted runner routing](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
10. [Helm provenance and integrity](https://helm.sh/docs/topics/provenance/)

## Release A — Kubernetes CSI VolumeSnapshot Contract Audit (93/100)

- Public self-contained code: https://github.com/Kanompung1988/k8s-volume-snapshot-contract-audit
- Source staging: `agent-skills` non-default branch `skill-lab/ep24-2026-11-17-snapshot-wheel`, `skills/k8s-volume-snapshot-contract-audit/`. Not present on portfolio default `main`.
- Authorized provisioning: [Bot_new_areazero PR #12](https://github.com/Kanompung1988/Bot_new_areazero/pull/12), [workflow #44002061297](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/44002061297) — **SUCCESS**, public repository default `main` verified.
- Standalone [release PR #1](https://github.com/Kanompung1988/k8s-volume-snapshot-contract-audit/pull/1) — **MERGED**. Last PR head `e2eeadfb0b921fc50f45bb22d55a1cb4ba227af4`.
- [PR workflow #44002253706](https://github.com/Kanompung1988/k8s-volume-snapshot-contract-audit/actions/runs/44002253706) — **SUCCESS**, two green jobs Python 3.10/3.12, **24 unit tests per version**, plus safe/review CLI fixtures, strict return-code assertion, frontmatter and SVG parse.
- Verified public default-branch `main` SHA: `49bd056ef78f2f472247cdd6ff52dfb02f9e1309`. [Post-merge main CI #44002323168](https://github.com/Kanompung1988/k8s-volume-snapshot-contract-audit/actions/runs/44002323168) — **SUCCESS**, Python 3.10/3.12.
- Boundaries: analyzes supplied local YAML only; no CSI driver, controller, cluster, CRD presence, actual snapshots, volume health or restore verification. Missing in-batch references are **review** findings (not claims the resource is absent from a cluster). `Delete` policy is a risk review, not intrinsically invalid. Does not guarantee backup durability or absence of data loss.

## Release B — Python Editable Wheel Metadata Parity Audit (91/100)

- Public self-contained code: https://github.com/Kanompung1988/py-editable-wheel-parity-audit
- Source staging: same non-default branch under `skills/py-editable-wheel-parity-audit/`. Not present on portfolio default `main`.
- Authorized provisioning: [Bot_new_areazero PR #11](https://github.com/Kanompung1988/Bot_new_areazero/pull/11), [workflow #44001595021](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/44001595021) — **SUCCESS**, public repository default `main` verified.
- Standalone [release PR #1](https://github.com/Kanompung1988/py-editable-wheel-parity-audit/pull/1) — **MERGED**. Last PR head `0cc9fd933fc65d2fba7b48c3130792ba9b725b72`.
- [PR workflow #44001701358](https://github.com/Kanompung1988/py-editable-wheel-parity-audit/actions/runs/44001701358) — **SUCCESS**, both Python 3.10 and 3.12 green with **16 unit tests per Python version** confirmed from GitHub job logs, real temporary-wheel CLI fixtures and frontmatter/SVG checks.
- Verified public default-branch `main` SHA: `f3208695b38f075d61095167e045647ed89243d7`. [Post-merge main CI #44002015262](https://github.com/Kanompung1988/py-editable-wheel-parity-audit/actions/runs/44002015262) — **SUCCESS**, two Python matrix jobs.
- Boundaries: read-only ZIP metadata inspection; no package imports, arbitrary code execution, build hook invocation, installed environment test, registry query or cryptographic validation. PEP 660 permits editable-only mechanism dependencies; these are reviewed, not automatically rejected unless `--strict`. Never distribute editable wheels.

## Provisioning, portfolio, quality and social safeguards

- Manifest `Bot_new_areazero/main:.github/skill-lab/repository-requests.json` retained all **20** prior entries and appended exactly **two** requests via reviewed PRs, for **22** total, with `source_ref` referencing full staged skills.
- Each independent repository contains root `SKILL.md`, English README, executable Python tool, fixtures, tests, MIT LICENSE, installation instructions for Claude Code/Codex, official references, original preserved Area Zero SVG, own hero illustration, CONTRIBUTING, BRAND, and real two-version GitHub Actions.
- Passing CI does not mean independent expert audit. Official `skills-ref` validator: **NOT_RUN**. External security review: **NOT_RUN**.
- **GitHub: CODE PUBLISHED, verified public and passing independent `main` CI.** **Instagram Skill Lab: OFF. Facebook Skill Lab: OFF.** No social posts created, modified, scheduled or published. **Daily AI Scout unchanged.**
