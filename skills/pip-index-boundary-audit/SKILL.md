---
name: pip-index-boundary-audit
description: Inspect local pip requirements files and nested constraints for extra package indexes, trusted hosts, plain HTTP, and root-escaping includes that warrant dependency-confusion review. Use before Python dependency installs or CI packaging changes; never install packages or disclose index credentials.
license: MIT
compatibility: Python 3.10+ standard library; offline, read-only, no network calls.
metadata:
  author: AREA ZERO
  version: "1.0.0"
---

# pip Index Boundary Audit

Use when reviewing Python `requirements.txt`, `-r` includes, `-c` constraints and private index settings before builds. The script does **not** install or resolve dependencies.

1. Ask for the root requirements path; run `python audit.py /path/to/requirements.txt --root /path/to/project --format json`.
2. Interpret exit 0 = no issue in files scanned, 1 = findings that need review, 2 = invalid invocation. NEVER paste index credentials or private URLs into reports; this tool outputs codes and relative paths only.
3. For `EXTRA_INDEX` or `MULTI_INDEX`, recommend explicit origin policy and trusted artifact mirroring, not naive index preference. For `TRUSTED_HOST` and `PLAIN_HTTP_INDEX`, inspect transport security.
4. Explain that `pip.conf`, environment variables, command-line flags and actual package resolution are **out of scope**; do not claim an installation was secure.
5. Run `python -m unittest discover -s tests -v` after editing parsing logic.

See [references/BEHAVIOR.md](references/BEHAVIOR.md) for sources, supported options, and limitations. Do not use for execution of pip commands or secret extraction.
