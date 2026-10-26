# AREAZERO Skill Lab — autonomous publishing contract

> [!IMPORTANT]
> **LATEST OWNER OVERRIDE (2026-10-25; applied to automation 2026-10-26): Skill Lab social publishing is OFF indefinitely.** Build, test, PR, and publish standalone GitHub code normally, but **do not create/schedule/enable/reschedule/publish posts on Instagram/Facebook**, via Metricool, workflows, or any service. Never turn a draft into autoPublish:true. Optional copy/artwork can exist only as offline DRAFT. This supersedes ALL older social instructions in this document and the bot playbook until the user explicitly reauthorizes Skill Lab social posting. Daily AI Scout is unaffected.

> **Thai series title:** ทำให้ AI เก่งขึ้นทุกวัน  
> **GitHub portfolio:** [Kanompung1988/agent-skills](https://github.com/Kanompung1988/agent-skills)  
> **Public code model:** **ONE SKILL = ONE DEDICATED PUBLIC REPOSITORY**, not a monorepo.  
> **Sibling editorial series:** Daily AI Scout (AI news/trends, not skill releases).

## Objectives

Build technical credibility for GitHub [@Kanompung1988](https://github.com/Kanompung1988) by shipping small, honestly tested open-source tools, with beautiful English GitHub documentation and one combined Thai daily recap when verified releases exist. If no skill passes quality gates, do not create filler content or fake releases.

## Repository responsibilities

- **Individual public repositories**: `Kanompung1988/<skill-slug>` contain all of that skill's `SKILL.md`, README, implementation, tests, examples, references, LICENSE, original logo and their own `.github/workflows/ci.yml`. Each repo accumulates its own Stars, Issues, CI history and contributions.
- **Public portfolio only**: `Kanompung1988/agent-skills` `main` contains human-readable directory/episode index and operating docs. **Do not add released Skill source folders to the portfolio default branch**.
- **Ephemeral staging**: for a new skill, stage its validated package on a *non-default branch* of `Kanompung1988/agent-skills` under `skills/<slug>/` (or use a separate authorized staging repository), then request repository provisioning. Keep it out of public `main`. Do not claim that staging is a public release.
- **Creation router**: GitHub Actions `Kanompung1988/Bot_new_areazero/.github/workflows/provision-skill-repos.yml` reads `.github/skill-lab/repository-requests.json` on `main` and uses server-side secret `AREAZERO_GITHUB_TOKEN` to create a PUBLIC repo idempotently. The request must contain `slug`, `source_path=skills/<slug>` and, for staging branches, `source_ref`. The workflow verifies that SKILL.md exists at that ref before creating a repo. **Do not send secrets in chat or public commits.**
- **Social image/log storage**: `Kanompung1988/Bot_new_areazero`, branch `areazero-social-assets` only. Never use its `main` branch for image posts. Do not use Google Drive.

## Daily autonomous production loop

1. Inspect latest [Social publishing playbook](https://github.com/Kanompung1988/Bot_new_areazero/blob/areazero-social-assets/AUTOMATION_PLAYBOOK.md), existing Metricool queue, today's agent-specific publication logs, this operations contract and all existing repos/episodes. Current timezone: `Asia/Bangkok`.
2. Research **8** concrete developer pain points. Score utility (25), distinctiveness (20), Claude/Codex relevance (15), feasibility (15), audience (10), demonstrability (10), social shareability (5), and reject near-duplicates. Editorial score **>=85/100** required; build 0–2 excellent skills only.
3. Implement one portable Agent Skill **per standalone repo**. Each package needs valid frontmatter `SKILL.md`, exact trigger/non-trigger guidance, step-by-step procedure, references, complete English README with original branded hero and unmodified Area Zero SVG logo, source/scripts, synthetic fixtures, tests, MIT code LICENSE and clear limitations/security/attribution. Optional dependencies must be documented. Use [agentskills.io/specification](https://agentskills.io/specification).
4. Test locally, report honest counts and any failures. If the `skills-ref` validator is not actually run, state `NOT_RUN`, not `PASSED`. Never claim external usage, unique invention or third-party review without evidence. Show a real CLI run and protect inputs/secrets.
5. Stage the complete package on a non-default `agent-skills` branch under `skills/<slug>/` and update the **authorized** repository-request manifest on `Bot_new_areazero/main` (only after checking idempotency and target repo existence). Use connector actions or GitHub Actions to provision. Confirm GitHub created exactly `Kanompung1988/<slug>` PUBLIC; do not substitute a different repo.
6. Populate the target repo on a feature branch and open a PR. CI on the **new standalone repo** must verify its tests and demo across supported Python versions. Compare actual latest head SHA and all job statuses; only merge after all gates truly pass. Then read `SKILL.md` and `README.md` back from the **public default branch**. A successful provisioning Action is not proof of published code.
7. Only then update this directory's README and [docs/EPISODES.md](EPISODES.md) with the verified repo links and CI. Never keep permanent duplicate copies of released source under the portfolio's `main`.
8. **SOCIAL OFF** — Do not call Metricool create/update/schedule/publish or GitHub social workflows for Skill Lab. Offline art or draft captions are optional only and must not be scheduled or uploaded for distribution.
9. Save verified code release evidence, PR/CI URLs and a clear social status **OFF** in GitHub documentation. If any prior scheduled draft exists, leave it unchanged; do not reactivate it.
10. Never interpret current GitHub publishing as permission for social publishing; only an explicit future owner instruction can restore it.

## Backlog and existing episode guard

- EP.01 was released on 2026-10-24 as *two standalone public repositories*, and its **single combined social post** has already been scheduled for **2026-10-25 12:00 ICT**, Metricool UUID `2137186428519728769`. **Do not create a second post for that day**. Consult live Metricool statuses; until public URL confirms publication report SCHEDULED/PENDING only.
- Daily AI Scout is independent. Keep its own content and idempotency keys separate; never alter it for Skill Lab releases.
- Do not split a two-skill episode into two overlapping marketing posts. Quality beats post frequency. If no new qualified public skills, produce a no-release report and stop rather than posting non-release filler.

## Tested release evidence (2026-10-24)

- Repository bootstrap: [GitHub Actions run #1](https://github.com/Kanompung1988/Bot_new_areazero/actions/runs/40092561794) created both public skill repositories.
- [OpenAPI independent CI](https://github.com/Kanompung1988/openapi-compat-audit/actions/runs/40093092063) — Python 3.10/3.12, 16 unit tests + 1 smoke per version, all passed.
- [CI Log Triage independent CI](https://github.com/Kanompung1988/ci-log-triage/actions/runs/40093094810) — Python 3.10/3.12, 16 unit tests + 1 smoke per version, all passed.
- Current original-logo SVG hashes are pinned in the standalone test suites; changes require explicit owner approval.
