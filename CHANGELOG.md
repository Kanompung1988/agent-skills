# Changelog

## 2026-10-24 — Standalone repository architecture

Migrated the two publicly released EP.01 Agent Skills into their own repositories:

- [openapi-compat-audit](https://github.com/Kanompung1988/openapi-compat-audit)
- [ci-log-triage](https://github.com/Kanompung1988/ci-log-triage)

Both were independently tested by GitHub Actions on Python 3.10 and 3.12 (16 unit checks and one CLI smoke case per repo and Python version). Converted this `agent-skills` project into a portfolio/episode directory only. Original release provenance remains [PR #1](https://github.com/Kanompung1988/agent-skills/pull/1).
