# openapi-compat-audit

**Predictable API contract change triage for coding agents.** Compares two OpenAPI 3.x specs locally and reports the evidence for likely breaking changes.

## Install

Copy this folder intact into your agent skills directory, or invoke the Python script directly. Requires Python 3.10+. For `.yaml` input, install `PyYAML` if your environment permits it; `.json` requires no external package.

## CLI

```bash
python3 scripts/compare_openapi.py --old old.json --new new.json --format markdown
python3 scripts/compare_openapi.py --old old.yaml --new new.yaml --format json --out /tmp/contract-check.json
```

Exit codes: `0` = no breaking finding or `--fail-on none`; `1` = invalid input; `2` = breaking finding (or any finding with `--fail-on any`). Full usage: `python3 scripts/compare_openapi.py --help`.

## What gets flagged

| Rule | Class | Why |
|---|---|---|
| Removed operation | breaking | Existing clients may invoke it. |
| New required query/header/path parameter | breaking | Previously valid calls may be rejected. |
| Newly required body or body property | breaking | Previously valid requests lack new fields. |
| Request enum narrowed | breaking | Old enum values now rejected. |
| Successful response status/media removed | breaking | Consumers may depend on it. |
| Removed required response property | breaking | Existing response contract no longer includes guaranteed data. |
| Type changes / composed schema refs | review | Need deeper semantic analysis. |
| Response enum expanded | review | Exhaustive client mappings may need updates. |

**Not checked:** auth, auth scope, server URL, discriminator semantics, all OpenAPI constraints, SDK-specific behavior or live endpoint behavior. Treat an empty result as *no issues detected*, not guaranteed backward compatibility.

## Test

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT, see this folder's LICENSE and repository LICENSE. No upstream text or scripts copied. API spec [Agent Skills](https://agentskills.io/specification).
