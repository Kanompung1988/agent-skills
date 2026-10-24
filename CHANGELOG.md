## Unreleased — Skill Lab automation hardening

- Adopted the **AREAZERO Skill Lab — Make AI more useful every day** series identity and linked the public episode catalog / daily release SOP.
- Replaced fixed two-skill CI test calls with a **dynamic discovery and test gate** for all new `skills/` subdirectories, including Python 3.10/3.12 matrix coverage.
- Added regression tests for missing README, license, test suites, invalid names and descriptions; continue preserving the official original Area Zero logo.
- Existing first release's public code and separate scheduled social launch remain unchanged.

# Changelog

## 2026-10-24 — Initial public-source release

- Two portable SKILL.md workflows: OpenAPI compatibility audit and CI log triage.
- Offline Python CLI implementations with synthetic examples and Markdown/JSON outputs.
- 22 focused unittest cases plus 10 distribution, documentation and brand checks; release-candidate local run verified on 2026-10-24.
- GitHub Actions Python 3.10/3.12 validation and reproducible example smoke test.
- Bilingual-friendly Area Zero visual identity in documentation; code and docs stay English.
- Explicit limitations, contribution guide, security policy and brand-license separation.

No GitHub release tag or external benchmark is implied by this changelog entry.