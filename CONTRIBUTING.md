# Contributing to Areazero Agent Skills

Thanks for making small, verifiable developer tools better. The best contribution includes a concrete failure case and a regression test.

## Before opening a pull request

1. Search existing issues to avoid duplicates. Include the skill name, affected rule, Python version and sanitized reproduction steps.
2. Keep each PR scoped to **one** behavior change or bug. Do not upload proprietary OpenAPI contracts, real user data or raw CI logs.
3. Add **synthetic fixtures** and a `unittest` that fails before your change and passes after it.
4. Update `SKILL.md`, a skill README and the relevant coverage/limitations reference whenever behavior changes.
5. Run all checks from repo root:

```bash
python3 -m compileall -q skills tests scripts
python3 -m unittest discover -s skills/openapi-compat-audit/tests -v
python3 -m unittest discover -s skills/ci-log-triage/tests -v
python3 -m unittest discover -s tests -v
python3 scripts/smoke_examples.py
```

A PR should state: **problem**, **smallest reproduction**, **change**, **test evidence**, **risk/limitations**, and any manually reviewed cases. Passing tests alone are not evidence of broad API or CI-tool coverage.

## Project expectations

- Python 3.10+; no network calls or new runtime dependencies without discussion.
- Preserve explicit CLI exit-code behavior and machine-readable output contracts.
- Do not execute arbitrary code from input files or CI logs.
- Treat redaction as a last layer, not authorization to publish sensitive logs.
- Never recolor/redraw official Area Zero SVG artwork or bundle it into other projects as though it were MIT-licensed.
- Keep documentation and code in English; synthetic examples only.

## Review and release

Open a feature branch and PR against `main`. The CI matrix runs on PR and push. Merging requires human review when external contributors are involved; automation must never falsely claim independent review or completed CI.

For private vulnerability reports, follow [SECURITY.md](SECURITY.md) rather than disclosing exploits in a public issue.
