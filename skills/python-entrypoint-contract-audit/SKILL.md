---
name: python-entrypoint-contract-audit
description: Validate pyproject.toml project.scripts and gui-scripts references, reserved entry-point groups, duplicate commands and optional local module targets without importing code. Use before publishing a Python package or when fixing missing command-line tools after installation.
---

# Python entry-point contract audit

## Trigger
Use when a developer wants to review `pyproject.toml` CLI entry points, troubleshoot why installed commands are missing, or check metadata before building a wheel. Do not use for arbitrary application code execution or to prove installed console scripts will actually run.

## Procedure
1. Locate the project's `pyproject.toml` and any `src/` modules.
2. Read `references/rules.md` for PEP 621 and PyPA entry-point rules.
3. Use Python 3.11+ or `python -m pip install tomli` for Python 3.10.
4. Run `python scripts/audit.py path/to/pyproject.toml --format json --strict`.
5. Explain `error` findings separately from `review` signals; a missing local target can be supplied by a dependency or generated during the build, so never assume its absence is a guaranteed packaging error.
6. Propose specific `pyproject.toml` corrections. Do not import, install, build, or execute untrusted projects to validate them.

## Safety and limitations
Read-only TOML up to 1 MB. Does not import package modules or execute entry points, build backends or package scripts. Checks module file existence only in root/ and src/; does not model namespace packages, editable installs, custom backend layouts or generated files. No assertion about callable existence or Python import resolution.

## Example
`python scripts/audit.py examples/review.toml --no-target-check --strict` reports duplicate `sample` command, invalid reference `sample.cli` and private `_main` review. Returns exit code 1.
