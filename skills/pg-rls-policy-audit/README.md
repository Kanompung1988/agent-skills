<p align="center"><img src="assets/area-zero-logo-full.svg" width="260" alt="Official unchanged Area Zero logo"></p>
<p align="center"><img src="assets/hero.svg" width="100%" alt="PostgreSQL RLS Policy Audit: original technical hero"></p>

# PostgreSQL RLS Policy Audit

**Declarations are not effective permissions.** Row-level security policies can exist while RLS is disabled; owners normally bypass RLS, and very broad policy predicates may unintentionally expose tenant rows.

[![CI](https://github.com/Kanompung1988/pg-rls-policy-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/pg-rls-policy-audit/actions/workflows/ci.yml) [![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20spec-00D9FF)](https://agentskills.io/specification) ![License](https://img.shields.io/badge/license-MIT-00FFA3)

## Why this exists
A focused read-only review tool with stable rule IDs, simple local CLI usage, synthetic fixtures, structured JSON output and honest boundaries. It does not phone home or modify the input. This is static analysis, not a certificate of production safety.

## Installation — Claude Code and Codex
Clone this **standalone repository**; install it under a supported skills folder for the relevant agent, such as project-local `.claude/skills/pg-rls-policy-audit/` for Claude Code or `.agents/skills/pg-rls-policy-audit/` for Codex. Keep `SKILL.md` at the top of the cloned directory and review scripts before running them.

```bash
git clone https://github.com/Kanompung1988/pg-rls-policy-audit.git
cd pg-rls-policy-audit
python -m pip --version
```

Python 3.10+ standard library only, no dependencies or database access.

## Quickstart and reproducible examples
```bash
python scripts/audit.py examples/safe.sql
python scripts/audit.py examples/review.sql --json
python -m unittest discover -s tests -v
```

Expected safe output:
```text
0 finding(s)
```

The **review** example intentionally returns exit code `1` and structured JSON `count > 0`. Exit code `2` means unreadable, overlarge or malformed input. All fixtures contain synthetic data.

Prompt your agent: *Use `pg-rls-policy-audit` to review this locally provided file, cite rule IDs and suggest minimal fixes. Do not make changes and do not assume production state.*

## Rules
Conservative token masking for strings, comments, dollar-quotes; DDL recognition for ALTER TABLE ENABLE/DISABLE/FORCE/NO FORCE and CREATE POLICY; review TO PUBLIC, literal USING(true), WITH CHECK(true), missing enable in supplied SQL, owner bypass and policy absence in supplied SQL.

## Repository layout
| File | Responsibility |
|---|---|
| `SKILL.md` | Agent Skills specification frontmatter, triggers and procedure |
| `scripts/audit.py` | Deterministic local read-only audit engine |
| `tests/test_audit.py` | Regression and boundary tests |
| `examples/` | Clean and intentionally problematic synthetic fixtures |
| `references/rules.md` | Precise coverage and cited technical references |
| `.github/workflows/ci.yml` | Matrix tests on Python 3.10 and 3.12 |
| `assets/` | Original SVG hero and exact owner-supplied Area Zero wordmark |

## Security and limitations
Only supplied DDL is checked; no catalog access, GRANT, BYPASSRLS, actual owner/role membership, ALTER POLICY, SQL execution, runtime policy evaluation, multi-file ordering or full PostgreSQL SQL grammar. Not shown in input does not mean missing in production. Inputs over 2 MB are rejected to avoid accidental bulk processing. Do not publish real secrets in GitHub issues; redact all reproduction inputs. The CLI does not execute inspected input. No production account is required. Code is released for review and improvement, not third-party security endorsement.

## Sources
1. https://www.postgresql.org/docs/current/ddl-rowsecurity.html
2. https://www.postgresql.org/docs/current/sql-createpolicy.html
3. https://www.postgresql.org/docs/current/sql-altertable.html

## Contributing, license, attribution
File issues with safe synthetic reproduction cases. Run unit tests and CLI fixtures before opening a PR. Code is MIT licensed. The **official Area Zero logo** is an unmodified owner-owned brand asset and is not relicensed under MIT. The hero artwork was created specifically for this skill.

Part of the [AREAZERO Skill Lab](https://github.com/Kanompung1988/agent-skills). Internal editorial review score **93/100** is not an external rating or adoption metric.
