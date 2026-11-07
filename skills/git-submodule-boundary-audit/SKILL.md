---
name: git-submodule-boundary-audit
description: Audit local Git submodule .gitmodules declarations against staged index gitlinks and flag unsafe source URLs or update tracking. Use when reviewing a repository with submodules or before merging changes to .gitmodules; never fetches or executes submodule code.
license: MIT
compatibility: Requires Python 3.10 or later and Git on PATH; offline, local-input read-only.
metadata:
  author: AREAZERO
  version: "1.0.0"
---

# Git submodule boundary audit

## Use when
- A developer or agent asks to inspect a local Git repo's submodules before merging a change.
- You can read local inputs and present specific, actionable review findings.

## Do not use when
- The user needs a definitive remote provenance, verified signatures or real-time upstream branch validation.
- Source input is missing, or analysis would require executing untrusted code, changing Git state or performing network operations.

## Procedure
1. Ask for or locate the relevant local Git repository and **staged** .gitmodules / gitlink entries.
2. Read [reference boundaries](references/REFERENCE.md) and explain that this is offline advisory analysis.
3. Run `python scripts/audit.py . --json`. JSON output is safe for automated parsing; code 0 = no findings, 1 = review findings, 2 = input error.
4. Report the code, affected resource/path, severity, and a minimal suggested change. Never assert complete security or runtime state.
5. Do **not** automatically edit deployment files, fetch submodules or deploy workloads. Request explicit authorization for modifications.

## Edge cases
- Absent .gitmodules, index gitlinks without declarations, relative upstream URLs, and branch tracking settings are handled. A branch setting is advisory: it does not make a Git gitlink unpinned.
- Never expose secrets from source; findings contain only normalized rules, resource names and paths.
