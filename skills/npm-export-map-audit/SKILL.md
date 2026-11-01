---
name: npm-export-map-audit
description: Use before publishing a Node.js package or reviewing changes to package.json exports; statically verify export mapping targets, subpath path rules and conditional mapping structure, and optionally check built files, without executing JavaScript, npm scripts or the Node module loader.
license: MIT
compatibility: Python 3.10+ standard library; local package.json only; network-free.
---

# Node Package Export Map Audit

## When to use
Use for package.json `exports` changes, npm package release checks, CommonJS/ESM conditional entrypoint reviews, and agent-generated package APIs.

## Do not use
Do not present this tool as a complete Node.js resolver, npm pack inspection, verification of dependencies, supply-chain scan, or validation of runtime import behavior.

## Procedure
1. Point the agent at a local `package.json` or package directory. Treat package scripts as data; do not execute them.
2. Read [references/MODEL.md](references/MODEL.md) for Node target rules and the difference between source and built-package checks.
3. Run `python scripts/audit.py examples/safe --format json`, then inspect the desired package with `python scripts/audit.py /path/to/package --format text --fail-on high`.
4. If checking a **completed build artifact**, add `--check-files`. Without a build, missing files are expected and are not classified by default.
5. Report each finding using its JSON code and location. Pattern exports are `REVIEW` because expansion and runtime resolution are not performed.
6. Recommend narrowly scoped changes; do not modify `package.json` or build/publish automatically.
7. Validate release behavior with the intended Node.js version and `npm pack --dry-run` separately if user authorizes it.

## CLI exit codes
0 threshold clear, 1 configured threshold reached, 2 malformed or unreadable input. No findings does not prove runtime compatibility.

## Safety
Only reads `package.json` metadata and optional path existence, without shell or Node execution, network access, or changes to the project.