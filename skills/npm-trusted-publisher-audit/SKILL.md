---
name: npm-trusted-publisher-audit
description: Review local package.json and GitHub Actions release workflows for npm trusted publishing prerequisites, OIDC permissions, eligible runners, publisher inventory mismatches, provenance suppression and token fallback. Use before an npm package release or when auditing publish CI; never as proof of actual npm registry configuration.
license: MIT
compatibility: Python 3.10+ and PyYAML 6.x; Claude Code or Codex. Offline and read-only.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# npm trusted publisher audit

## Trigger
- Audit a package release workflow before switching from npm write tokens to OIDC.
- Review CI for id-token permission and provenance configuration.
- Compare repository metadata to a human-provided trusted-publisher inventory.

## Do not trigger
- To claim npmjs.com actually trusts the current publisher.
- To verify live OIDC attestation, the published package or npm CLI version.
- To execute or approve a publish.

## Steps
1. Identify an authorized local project with package.json and .github/workflows.
2. Optionally add trusted-publisher.json with repository and workflow fields copied from a manually inspected npm publisher setup. The inventory is not verified by this script.
3. Install the dependencies from requirements.txt in the skill repository.
4. Run python scripts/audit.py PATH_TO_PROJECT --json.
5. Interpret exit 0 as no static findings, exit 1 as manual review, exit 2 as input error.
6. Map rule IDs to references/REFERENCE.md, inspect actual npm package Trusted Publisher settings and run a controlled publishing rehearsal.
7. Never print secrets or execute suspect publish commands.

## Limits
Recognizes direct npm publish and npm stage publish run steps only; does not model shell execution, action wrappers or conditional job reachability. Offline deterministic static review is not a registry security certification.
