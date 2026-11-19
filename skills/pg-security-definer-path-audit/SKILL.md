---
name: pg-security-definer-path-audit
description: Examine local PostgreSQL CREATE FUNCTION and CREATE PROCEDURE SQL for SECURITY DEFINER routines with missing or risky function-level search_path. Use during privileged database function reviews and migration PRs; never connects to databases or runs SQL.
license: MIT
compatibility: Python 3.10 or newer; standard library only, no network or database access
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# PostgreSQL SECURITY DEFINER Path Audit

## Use when

- Reviewing privileged PostgreSQL migration definitions before applying them.
- Looking for missing function-level `SET search_path` on `SECURITY DEFINER` routines.
- Reviewing `pg_temp` ordering and potentially untrusted schemas in search paths.

**Do not use** as a substitute for a live privilege audit, SQL parser, object name resolution, `PUBLIC` EXECUTE privilege review, or validation of schema ACLs. No SQL is executed.

## Procedure

1. Obtain a SQL source file without production credentials.
2. Run `python scripts/audit.py /path/to/migration.sql --format json` (add `--strict` to exit 2 on findings).
3. Review each reported routine at the line number; `MISSING_SEARCH_PATH` is a high-priority review, other codes need schema ACL and PostgreSQL-version context.
4. When remediating, explicitly place trusted schemas first and `pg_temp` last per PostgreSQL guidance. Inspect default `PUBLIC` function execution privileges and grant policy separately.
5. If parsing is uncertain (quoted schema identifiers, dynamic search paths, complex SQL, altered functions), record a manual review rather than assuming safety.
6. Report findings and what was not inspected; do not claim that absence of findings proves a function is secure.

See [reference and limits](references/REFERENCE.md). Synthetic examples: `fixtures/safe.sql` and `fixtures/review.sql`.
