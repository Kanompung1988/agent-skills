---
name: otel-http-semconv-audit
description: Audit sanitized OpenTelemetry OTLP JSON spans for legacy versus stable HTTP semantic-convention attribute names, accidental dual emission, stated http mode conflicts, and possible high-cardinality http.route patterns. Use during HTTP instrumentation upgrades or observability dashboard migration; never claim live telemetry completeness.
license: MIT
compatibility: Python 3.10+; offline JSON only. Claude Code and Codex.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# OpenTelemetry HTTP semantic convention audit

## Trigger
- Review a sanitized export of HTTP spans before migrating from pre-stable HTTP semantic conventions.
- Identify legacy HTTP attribute keys used by instrumentation or queries.
- Check whether the sample agrees with a declared OTEL_SEMCONV_STABILITY_OPT_IN mode.

## Do not trigger
- To query a live telemetry backend or validate actual resource configurations.
- To estimate cardinality or cost from a partial trace sample.
- To publish telemetry or expose sensitive attribute values.

## Steps
1. Request a sanitized, authorized local OTLP JSON span export; redact tokens, URLs and personally identifying attribute values before using this skill.
2. Run python scripts/audit.py PATH_TO_SANITIZED_JSON --json.
3. If the user can verify the rollout flag, add --stability-opt-in http or --stability-opt-in http/dup; otherwise leave the default unknown.
4. Interpret exit 0 as no findings in this input sample, exit 1 as review findings and exit 2 as invalid input.
5. Map rule IDs using references/REFERENCE.md and compare to the OpenTelemetry specification in references/SOURCES.md.
6. Correct instrumentation and dashboards with measured rollout validation; never infer global production completeness from a single sample.

## Limits
Input JSON may be flat spans or standard OTLP resourceSpans/scopeSpans. The tool never exports attribute values and does not connect to a telemetry backend. HTTP route issues are heuristics; absence of a finding cannot prove low cardinality.
