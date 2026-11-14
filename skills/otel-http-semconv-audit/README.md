<p align="center"><img src="assets/areazero-logo.svg" width="220" alt="Original AREAZERO identity"></p>
<p align="center"><img src="assets/hero.svg" width="100%" alt="OpenTelemetry HTTP semantic convention migration review"></p>

# OpenTelemetry HTTP Semantic Convention Audit

**Make HTTP telemetry migrations reviewable without leaking trace values.** This portable Agent Skill reads sanitized OTLP JSON and reports legacy HTTP attributes, accidental old/new coexistence, stability-opt-in conflicts and suspected raw identifiers in http.route. No network connections, no raw attribute values in findings.

## Install and demo

~~~bash
git clone https://github.com/Kanompung1988/otel-http-semconv-audit.git
cd otel-http-semconv-audit
python scripts/audit.py examples/safe.json --json
python scripts/audit.py examples/review.json --json       # review findings, exit 1
python scripts/audit.py examples/review.json --stability-opt-in http/dup --json
python -m unittest discover -s tests -v
~~~

**Claude Code:** clone repository into .claude/skills/otel-http-semconv-audit.
**Codex:** clone into .agents/skills/otel-http-semconv-audit.
Ask the agent to follow SKILL.md, sanitize input and inspect local trace export only.

## Input, result and risk boundaries

Supports a JSON object containing spans or OTLP resourceSpans/scopeSpans arrays; max 4 MiB and 10,000 spans. Exit 0 = no findings for examined sample, 1 = findings, 2 = input error. Output includes only stable rule IDs, keys and span indexes; no attribute values. The existence of legacy names alone does not prove a migration is wrong if dual emission is intentionally enabled.

[Rule reference](references/REFERENCE.md) · [Official sources](references/SOURCES.md) · [MIT code license](LICENSE). Original AREAZERO artwork is independent trademark material and excluded from code licensing. This static reviewer is not an OTel backend, a cardinality analyzer or a deployment guarantee.
