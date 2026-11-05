---
name: npm-lifecycle-policy-audit
description: Inspects local npm package.json lifecycle hooks for implicit install, CI, pack and publish execution paths and binding.gyp fallback. Use before adding npm dependencies, running npm ci/install, packaging or publishing Node packages. Do not use to execute scripts, determine malicious intent or certify supply-chain safety.
license: MIT
compatibility: Python 3.10+; offline, read-only, no npm installation required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# npm Lifecycle Script Policy Audit

## When to activate
Use when reviewing a local Node.js package before an install/ci/pack/publish action, or when a user needs a clear list of implicitly triggered lifecycle hooks. Do not use as a sandbox, virus scanner, or registry provenance verifier.

## Procedure
1. Read [rule map](references/rules.md) and identify the specific authorized `package.json` location. This audit is intentionally one package at a time; workspaces and dependencies require individually scoped reviews.
2. Run `python scripts/audit.py examples/safe/` to confirm the tool executes safely, without npm.
3. Run `python scripts/audit.py PATH --json` on an approved local package manifest. Never execute a discovered lifecycle command.
4. Explain return codes: **0** no modeled findings, **1** lifecycle hook review required, **2** invalid/unsafe input.
5. Investigate each hook's purpose and caller context; a lifecycle script is **not** inherently malicious.
6. Use `--allow prepare` only after the user explicitly approves that hook, recording the reason separately. The option filters a report, not npm behavior.
7. If uncertain, recommend a separate human-approved npm dry run in a sandbox; do not install packages or change scripts on your own.

## Verification
```bash
python -m unittest discover -s tests -v
python scripts/audit.py examples/safe/
python scripts/audit.py examples/review/ --json
```

The scanner never evaluates script values or contacts npm, and keeps command bodies out of findings.
