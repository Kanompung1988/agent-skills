# AREAZERO Skill Lab — EP.10 candidate research and release evidence
**Date:** 2026-11-03 (Asia/Bangkok) · **Code release:** PUBLIC · **Skill Lab social:** OFF, owner override 2026-10-25

## Scoring model
Useful developer pain (25), distinctiveness relative to the 18 previously shipped Skills (20), Claude Code/Codex fit (15), feasible bounded implementation (15), developer audience (10), demonstrable tests (10), social clarity (5). Total /100. These are internal editorial scores, not adoption metrics or independent assessments. Release only >=85 and tested, up to two. No quota-forced filler.

| Candidate and concrete pain | Utility /25 | Originality /20 | Agent fit /15 | Feasibility /15 | Audience /10 | Test/demo /10 | Communication /5 | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Kubernetes policy/v1 PodDisruptionBudget: accidental empty selectors, overlapping explicit Pod matches, invalid availability fields | 24 | 18 | 14 | 15 | 9 | 9 | 4 | **93** | RELEASE |
| Python pip requirements: extra indexes, plain HTTP, trusted hosts and nested include trust boundaries | 25 | 18 | 14 | 15 | 9 | 9 | 4 | **94** | RELEASE |
| Docker Compose writable host bind mounts and ro/rw ambiguity | 23 | 13 | 13 | 13 | 9 | 8 | 4 | **83** | Reject: overlaps existing Compose port audit and Docker context guard |
| npm lifecycle scripts and pre/post install policy | 22 | 15 | 12 | 13 | 8 | 8 | 4 | **82** | Defer: npm v11 semantics and noisy false positives need broader tests |
| GitHub artifact attestation enforcement readiness | 22 | 14 | 12 | 13 | 9 | 8 | 4 | **82** | Defer: reliable signature verification requires upstream CLI/online trust |
| Kubernetes Pod SecurityContext privilege drift | 22 | 12 | 13 | 14 | 8 | 8 | 4 | **81** | Defer: overlaps existing security review toolbox; context-dependent admission |
| Git submodule URLs and reproducible provenance | 20 | 13 | 13 | 13 | 8 | 8 | 4 | **79** | Defer: source URL alone does not establish commit trust |
| GitHub reusable workflow permissions/secrets inheritance | 21 | 11 | 12 | 14 | 8 | 9 | 4 | **79** | Defer: strong near-duplicate of GHA Trust Boundary Audit |

## Primary-source references (retrieved/checked 2026-11-03)
1. [Kubernetes PodDisruptionBudget configuration](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) — empty `policy/v1` selector matches all Pods in its namespace, null selector none; one availability field.
2. [pip install — index security warning](https://pip.pypa.io/en/stable/cli/pip_install/) — `--extra-index-url` can enable dependency confusion.
3. [Docker Compose service mounts](https://docs.docker.com/reference/compose-file/services/) — bind/volume types and ro/rw default.
4. [npm lifecycle scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/) — install, prepare, pack and publish events.
5. [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) — generation and verification boundaries.
6. [Kubernetes container SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/).
7. [Git .gitmodules documentation](https://git-scm.com/docs/gitmodules.html).
8. [GitHub reusing workflows](https://docs.github.com/en/actions/how-tos/sharing-automations/reuse-workflows).

## EP.10 release evidence — exact verified commits and runs
- **Kubernetes PDB Scope Audit**: [public repo](https://github.com/Kanompung1988/k8s-pdb-scope-audit), [merged PR #1](https://github.com/Kanompung1988/k8s-pdb-scope-audit/pull/1), [PR CI #41565543495](https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/runs/41565543495) and [post-merge main CI #41565658589](https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/runs/41565658589). Initial public main SHA `9da8ff8f4d0fdb75e5aa0c26b5d46d67e81f17de`. Python 3.10/3.12 two jobs PASS, CLI safe=0/review=1, frontmatter check PASS; 20/20 local Python 3.13 unit tests.
- **pip Index Boundary Audit**: [public repo](https://github.com/Kanompung1988/pip-index-boundary-audit), [merged PR #1](https://github.com/Kanompung1988/pip-index-boundary-audit/pull/1), [PR CI #41565552331](https://github.com/Kanompung1988/pip-index-boundary-audit/actions/runs/41565552331) and [post-merge main CI #41565665585](https://github.com/Kanompung1988/pip-index-boundary-audit/actions/runs/41565665585). Initial public main SHA `949f26e0a557d2c246573ccf25b68b5e799b5162`. Python 3.10/3.12 two jobs PASS, CLI safe=0/review=1, frontmatter check PASS; 20/20 local Python 3.13 unit tests.
- [Repo provisioner #41565377888 SUCCESS](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/41565377888), manifest main commit `841cc755d02d34d6accc2a639bd792cdb710e225`, staging branch `skill-lab/ep10-2026-11-03-pdb-pip`. A provisioner success alone was not treated as release: both public default-branch README.md and SKILL.md were fetched after merge.

## Final reviewed documentation release (2026-11-03)

To display the actual new hero artwork and the unmodified owner-supplied AREA ZERO logo inside both GitHub READMEs, each repository received a separate docs-only PR **after** initial code release:

- [PDB README polish PR #2](https://github.com/Kanompung1988/k8s-pdb-scope-audit/pull/2) — [latest post-merge main CI SUCCESS #41566232466](https://github.com/Kanompung1988/k8s-pdb-scope-audit/actions/runs/41566232466), **current public `main` SHA `e9d760ee8d041f13853e622fbe9a954dd39908ac`**.
- [pip README polish PR #2](https://github.com/Kanompung1988/pip-index-boundary-audit/pull/2) — [latest post-merge main CI SUCCESS #41566240807](https://github.com/Kanompung1988/pip-index-boundary-audit/actions/runs/41566240807), **current public `main` SHA `9ff2d6c98e246de856cf898a4658a96e9c84eb21`**.

Each latest CI matrix is green for Python 3.10 and 3.12, including tests, example CLI fixtures and skill frontmatter checks. Both public default-branch README.md files were read back to verify `assets/hero.svg` and `assets/logo-full.svg` embeds, and both root SKILL.md files were fetched and verified. Brand logo remains an owner-supplied asset, not an invented generative replacement.

## Safety and uncertainty
PDB matching is confined to explicit Pod objects in the supplied manifest: no live pods, Deployment templates, API admission or `disruptionsAllowed`. pip parsing covers local requirements and nested `-r`/`-c` files, not `pip.conf`, shell/environment flags or actual resolution. Both are read-only. No claim of complete vulnerability detection, external adoption, independent review, or live production correctness.

**Official skills-ref validator:** NOT_RUN (not installed in local environment). Local tests used Python 3.13. Both GitHub Actions workflows verified on 3.10 and 3.12. Social content was not created, scheduled, or posted. Daily AI Scout was not changed.
