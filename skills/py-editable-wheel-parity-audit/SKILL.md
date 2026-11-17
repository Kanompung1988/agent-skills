---
name: py-editable-wheel-parity-audit
description: "Compare local regular and PEP 660 editable Python wheel metadata for Name, Version, Requires-Dist, entry points and core metadata drift. Use before package releases and when editable installs differ from wheel builds."
license: MIT
compatibility: "Python 3.10+ standard library. Offline; expects locally built regular and ephemeral editable wheel files."
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Python Editable Wheel Metadata Parity Audit

Trigger for PEP 660 editable versus regular wheel packaging problems. Do not use to claim import parity, run backend hooks or publish editable wheels; those are temporary artifacts.

1. Obtain two authorized locally generated wheels (normal and PEP 660 editable). Never use live secrets or distribute the editable wheel.
2. Read [reference](references/REFERENCE.md) for PEP 660 exceptions.
3. Execute `python audit.py normal.whl editable.whl --format json --strict`.
4. Optionally allow explicitly justified editable mechanism dependencies with `--allow-extra editables` (exact Requires-Dist string).
5. Report matched identities, concrete finding codes and human checks. Exit 0 = no errors, 2 = errors (or review findings in strict mode), 1 = invalid input.
6. Read-only ZIP metadata analysis: no code execution, archive extraction or registry access. Does not test runtime imports or compare semantic PEP 508 expressions.
