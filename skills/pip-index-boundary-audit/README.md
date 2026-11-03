# pip Index Boundary Audit

**Review dependency origin boundaries before `pip install`.** A portable, fully offline Agent Skill that inspects requirements/index configuration *inside explicitly provided files* without resolving packages or leaking credentials.

[![CI](https://github.com/Kanompung1988/pip-index-boundary-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/pip-index-boundary-audit/actions/workflows/ci.yml) · [Agent Skills specification](https://agentskills.io/specification) · MIT

## Install as a skill

**Claude Code:** `git clone https://github.com/Kanompung1988/pip-index-boundary-audit.git .claude/skills/pip-index-boundary-audit`  
**Codex:** `git clone https://github.com/Kanompung1988/pip-index-boundary-audit.git .agents/skills/pip-index-boundary-audit`

Requires Python 3.10+ and standard library only; it never invokes pip itself.

## Quickstart

```bash
python audit.py examples/review.txt --format json
python audit.py examples/safe.txt
python -m unittest discover -s tests -v
```

`examples/review.txt` intentionally returns exit **1** for `EXTRA_INDEX`, `MULTI_INDEX` and `TRUSTED_HOST`. `examples/safe.txt` returns exit **0**. Exit **2** is a failed input invocation. Examples use synthetic `.invalid` hosts and no actual secrets.

## What it checks

`--extra-index-url` (dependency confusion), simultaneous indexes, unencrypted HTTP index, `--trusted-host`, nested `-r`/`-c` includes, path escape attempts and unreadable files. The output contains only finding codes and relative path/line references—never URL values or credentials.

## Limits and security

This is not a full pip parser/resolver and does not inspect pip.conf, environment variables, shell flags or installed artifacts. It does not block installs, execute commands, or query remote hosts. A clean report does **not** guarantee artifact provenance. Restrict the scan root to a trusted project and review warnings rather than applying changes automatically. Reference: [pip's index safety warning](https://pip.pypa.io/en/stable/cli/pip_install/).

## Contributing and license

Open an issue with a redacted requirements fixture; add tests for parser changes and preserve the no-credential-output rule. CI tests Python 3.10/3.12. MIT License (see `LICENSE`). Author: AREA ZERO, 2026. Not affiliated with PyPA.
