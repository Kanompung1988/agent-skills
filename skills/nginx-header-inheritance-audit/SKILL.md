---
name: nginx-header-inheritance-audit
description: Review local NGINX configuration for security response headers silently lost through add_header inheritance or add_header_inherit overrides. Use for reverse-proxy config changes and pre-deployment header reviews. Do not use as a live HTTP/TLS security scanner or as a substitute for nginx -t.
license: MIT
compatibility: Python 3.10+, local filesystem; read-only, no network.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# NGINX Header Inheritance Audit

## Trigger / non-trigger
Use when an authorized user supplies nginx configuration and asks why headers disappeared in nested `http/server/location/if` scopes or requests a local header-inheritance audit. Do not use to edit configs or claim real response headers, live server behavior, certificate state, or security compliance.

## Procedure
1. Read [rules and caveats](references/rules.md), particularly version-specific `add_header_inherit` behavior since 1.29.3.
2. Read only the provided configuration. Never automatically recurse through includes or read credentials.
3. Run `python scripts/audit.py examples/safe.conf` (exit 0).
4. Run `python scripts/audit.py PATH --json`; add `--nginx-version 1.29.3` only if the deployed version is known.
5. Interpret 0 = no modeled findings, 1 = review required, 2 = invalid file/input. Cite rule IDs and line numbers.
6. Prioritize NGH001 lost inherited security headers and NGH003 unexpanded includes. Recommend `nginx -t` and `curl` against staging as separate operator-controlled verification.
7. Never say a clean result proves TLS/HTTP safety. Suggest minimal fixes but do not mutate the input without approval.

## QA
```bash
python -m unittest discover -s tests -v
python scripts/audit.py examples/safe.conf
python scripts/audit.py examples/review.conf --json
```

No third-party Python packages, server contact, or inspected-config execution required.
