---
name: py-dependency-group-audit
description: Checks local PEP 735 dependency groups in pyproject.toml for normalized-name collisions, invalid requirements, malformed includes, missing targets and cycles. Use when reviewing or migrating Python development dependency groups. Do not use to resolve/install dependencies, audit indexes or validate lockfiles.
license: MIT
compatibility: Python 3.10+ on a local filesystem.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Python Dependency Group Audit

## When to use
Use only when the user asks for a bounded, offline review of local pep 735 / pyproject contracts files. Do not invoke to certify security, modify production, fetch secrets, install software, or inspect an unapproved file.

## Workflow
1. Read `references/rules.md` and identify whether the user's local input falls within the supported grammar.
2. Request approval before installing prerequisites, if not already present. Python 3.10+; run `pip install -r requirements.txt` for packaging and Python 3.10's tomli.
3. Run `python scripts/audit.py examples/safe.toml` to confirm the test fixture returns `0 finding(s)`.
4. Run `python scripts/audit.py PATH --json` with the authorized input PATH.
5. Interpret return codes: **0** no modeled findings, **1** review findings, **2** unreadable/invalid input.
6. For each rule ID, explain why it may matter, evidence supplied by this static input, likely false positives, and minimal remediation. Never claim a complete production audit.
7. Avoid leaking configuration, SQL data or dependency URLs. Do not upload source input to remote services.
8. Propose safe changes for human review, but do not write changes without explicit approval. Re-run checks after approved changes.

## Local verification
```bash
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.toml
python scripts/audit.py examples/review.toml --json
python -m unittest discover -s tests -v
```

## Coverage
Normalized names (PEP 503 style), strict list values, valid PEP 508 requirements using PyPA packaging, include-group object shape, normalized target lookup and acyclic include graphs.

## Limits
Does not install packages, resolve versions, inspect package registries, install from requirements files, or compare lockfiles. Invalid input values are not echoed, since dependency URLs can contain credentials. A clean report does not establish compatible dependencies.

This skill does not contact a live service or execute the inspected input.
