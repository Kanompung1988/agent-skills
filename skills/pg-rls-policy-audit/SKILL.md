---
name: pg-rls-policy-audit
description: Reviews supplied local PostgreSQL SQL DDL for RLS ENABLE/DISABLE/FORCE, CREATE POLICY, PUBLIC scope and literal true predicates. Use when reviewing SQL migrations or row-level security policy diffs. Not for live PostgreSQL effective-permission verification or arbitrary SQL dialects.
license: MIT
compatibility: Python 3.10+ on a local filesystem.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# PostgreSQL RLS Policy Audit

## When to use
Use only when the user asks for a bounded, offline review of local postgresql / row access files. Do not invoke to certify security, modify production, fetch secrets, install software, or inspect an unapproved file.

## Workflow
1. Read `references/rules.md` and identify whether the user's local input falls within the supported grammar.
2. Request approval before installing prerequisites, if not already present. Python 3.10+ standard library only, no dependencies or database access.
3. Run `python scripts/audit.py examples/safe.sql` to confirm the test fixture returns `0 finding(s)`.
4. Run `python scripts/audit.py PATH --json` with the authorized input PATH.
5. Interpret return codes: **0** no modeled findings, **1** review findings, **2** unreadable/invalid input.
6. For each rule ID, explain why it may matter, evidence supplied by this static input, likely false positives, and minimal remediation. Never claim a complete production audit.
7. Avoid leaking configuration, SQL data or dependency URLs. Do not upload source input to remote services.
8. Propose safe changes for human review, but do not write changes without explicit approval. Re-run checks after approved changes.

## Local verification
```bash
python -m pip --version
python scripts/audit.py examples/safe.sql
python scripts/audit.py examples/review.sql --json
python -m unittest discover -s tests -v
```

## Coverage
Conservative token masking for strings, comments, dollar-quotes; DDL recognition for ALTER TABLE ENABLE/DISABLE/FORCE/NO FORCE and CREATE POLICY; review TO PUBLIC, literal USING(true), WITH CHECK(true), missing enable in supplied SQL, owner bypass and policy absence in supplied SQL.

## Limits
Only supplied DDL is checked; no catalog access, GRANT, BYPASSRLS, actual owner/role membership, ALTER POLICY, SQL execution, runtime policy evaluation, multi-file ordering or full PostgreSQL SQL grammar. Not shown in input does not mean missing in production.

This skill does not contact a live service or execute the inspected input.
