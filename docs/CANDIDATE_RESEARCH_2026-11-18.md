# AREAZERO Skill Lab — EP.25 · 18 November 2026 (Asia/Bangkok)

**GitHub code: two independent public releases, latest main CI SUCCESS.** **Skill Lab social: OFF indefinitely** for Instagram @areazero.ai and Facebook AreaZero. No social scheduling, posting or drafts modified. Daily AI Scout unchanged.

## Eight screened developer pain points

Editorial score: usefulness /25 + distinctiveness against 48 released skills /20 + Agent fit /15 + feasibility /15 + audience /10 + reproducible demo /10 + communication /5. The numbers are internal assessments, not externally measured adoption or security assurance. The publishing threshold is >=85/100 and passing tests + verified public standalone main CI.

| Problem | Utility | Distinct | Agent | Feasible | Audience | Demo | Share | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Local GitHub Actions reusable workflow caller and workflow_call interface mismatch (inputs, secrets, types) | 24 | 19 | 14 | 14 | 9 | 10 | 4 | **94** | RELEASE |
| Kubernetes Ingress TLS host/rule drift and in-batch same-namespace Secret type/key problems | 23 | 18 | 14 | 14 | 9 | 10 | 4 | **92** | RELEASE |
| Renovate lockFileMaintenance colliding with package-update schedule | 20 | 15 | 12 | 12 | 8 | 9 | 4 | 80 | DEFER: manager/schedule semantics |
| GitHub self-hosted runner labels/groups mismatch | 20 | 14 | 13 | 12 | 8 | 9 | 3 | 79 | DEFER: live inventory needed |
| Sigstore/cosign identity/issuer verification mistakes | 20 | 14 | 12 | 12 | 8 | 9 | 4 | 79 | DEFER: real cryptographic verification |
| Gateway API route observedGeneration status freshness | 20 | 14 | 12 | 12 | 8 | 8 | 4 | 78 | DEFER: live controller observation |
| Helm OCI provenance and chart identity validation | 19 | 14 | 12 | 12 | 8 | 9 | 3 | 77 | DEFER: keyring/signatures needed |
| Argo Rollouts Analysis argument template drift | 19 | 12 | 12 | 12 | 8 | 8 | 3 | 74 | REJECT: overlap with earlier Rollouts skill |

The released reusable-input auditor is different from the existing reusable-permissions skill; this Ingress TLS reviewer is different from Service backend and Gateway ReferenceGrant audits. Both operate on synthetic local files with no credentials or live infrastructure effects.

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Reusable workflow documentation](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
- [workflow_call syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Kubernetes Ingress TLS](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress API reference](https://kubernetes.io/docs/reference/kubernetes-api/networking/ingress-v1/)
- [Renovate config](https://docs.renovatebot.com/configuration-options/#lockfilemaintenance)
- [GitHub runner routing](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
- [Sigstore cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/)
- [Gateway API specification](https://gateway-api.sigs.k8s.io/reference/spec/)
- [Helm provenance](https://helm.sh/docs/topics/provenance/)

## Release evidence

**Provisioning**: Both full skill packages staged only on nondefault portfolio branch `skill-lab/ep25-2026-11-18-reusable-ingress`. [Authorized repository-request PR #13](https://github.com/Kanompung1988/Bot_new_areazero/pull/13) merged; [provisioning Actions #44220890363](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/44220890363) SUCCESS. All 22 preexisting idempotency records retained; 24 records total.

**A — GitHub Actions Reusable Input Contract Audit (94/100)**: [Standalone PUBLIC repo](https://github.com/Kanompung1988/gha-reusable-input-contract-audit), [release PR #1](https://github.com/Kanompung1988/gha-reusable-input-contract-audit/pull/1) MERGED, [quality PR #2](https://github.com/Kanompung1988/gha-reusable-input-contract-audit/pull/2) MERGED. [Post-merge main CI #44221433057](https://github.com/Kanompung1988/gha-reusable-input-contract-audit/actions/runs/44221433057) SUCCESS (Python 3.10/3.12; 20 unit tests per version and safe/review CLI smoke). Verified public default `main` SHA `0eb3c3f25f70bdf20d2e95b89a4c43b0f4f29e9f`.

**B — Kubernetes Ingress TLS Contract Audit (92/100)**: [Standalone PUBLIC repo](https://github.com/Kanompung1988/k8s-ingress-tls-contract-audit), [release PR #1](https://github.com/Kanompung1988/k8s-ingress-tls-contract-audit/pull/1) MERGED, [quality PR #2](https://github.com/Kanompung1988/k8s-ingress-tls-contract-audit/pull/2) MERGED. [Post-merge main CI #44221441998](https://github.com/Kanompung1988/k8s-ingress-tls-contract-audit/actions/runs/44221441998) SUCCESS (Python 3.10/3.12; 20 unit tests per version and safe/review CLI smoke). Verified public default `main` SHA `d7a167832eaebf1bc018e229dbb1e82a553f5132`.

Both standalone repos include root SKILL.md, English README, Claude Code/Codex instructions, Python CLI, synthetic fixtures, tests, MIT license, dependencies, references, original unchanged AREAZERO SVG with SHA256 CI check, hero SVG, and separate CI. Local Python tests: 20/20 for each. Independent external review: NOT_RUN. Official `skills-ref` validation: NOT_RUN.

**Limits:** GHA audit resolves same-repo local workflows only; it does not evaluate dynamic expressions or live secret presence. TLS audit treats missing Secret in a provided batch as review-only; no certificate, controller or cluster handshake checks. Actual production safety is not guaranteed.

**GitHub code PUBLISHED. Skill Lab Instagram OFF. Skill Lab Facebook OFF. Daily AI Scout unchanged.**
