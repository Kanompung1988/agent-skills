<p align="center"><img src="assets/areazero-logo.svg" width="270" alt="Original Area Zero brand mark"></p>

# Gateway API ReferenceGrant Audit

**Catch missing cross-namespace trust grants before a Gateway API deployment.**

[![Independent CI](https://github.com/Kanompung1988/gateway-referencegrant-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Kanompung1988/gateway-referencegrant-audit/actions/workflows/ci.yml) · MIT · Python 3.10+

## Why it exists

A Route targeting a Service in another namespace, or a Gateway referencing a TLS Secret in another namespace, ordinarily requires a matching `ReferenceGrant` **in the target namespace**. A correctly spelled grant in the wrong namespace or with the wrong `from.kind` can be silently overlooked in reviews. This tool reads local, rendered YAML and reports bounded findings before rollout.

## Quick start

```bash
git clone https://github.com/Kanompung1988/gateway-referencegrant-audit.git
cd gateway-referencegrant-audit
python -m pip install 'PyYAML>=6,<7'
python scripts/audit.py examples/safe.yaml --json      # zero findings, exit 0
python scripts/audit.py examples/review.yaml --json    # review findings, exit 1
python scripts/audit.py ./manifests --json
python -m unittest discover -s tests -v
```

Outputs JSON with `count` and `findings`: `code`, `severity`, `resource`, `file`, `message`, `remediation`. CLI exits: 0 clean input scope, 1 review findings, 2 invalid input. Data is never submitted to an API. Do not include credentials in manifest bundles.

## Install as an Agent Skill

**Claude Code**: `git clone https://github.com/Kanompung1988/gateway-referencegrant-audit.git ~/.claude/skills/gateway-referencegrant-audit`

**Codex**: `git clone https://github.com/Kanompung1988/gateway-referencegrant-audit.git ~/.agents/skills/gateway-referencegrant-audit`

Clone the entire repository so `SKILL.md` and `scripts/` share one root. Reopen or reload agent skills to discover it. Format: https://agentskills.io/specification.

## Coverage and limitations

- Detects missing cross-namespace grants for HTTP/GRPC/TCP/TLS/UDP Route backendRefs, HTTP request mirrors, and Gateway TLS certificateRefs.
- Resolves `from` source namespace/kind and `to` target kind/group/name against supplied ReferenceGrant objects. `to.name` omitted is a legitimate broad grant.
- Route `parentRefs` and mesh-only Service parents are not treated as Gateway backend references. Some mesh implementations have different reference rules; verify manually.
- Does not inspect live clusters, Gateway AllowedRoutes, RBAC, admission checks, resource existence, or controller-specific extension refs. Missing *local* grants do not prove missing *live* grants.
- Uses bounded file size/count, safe YAML parsing and no shell execution of manifests. The analyzer is advisory, not a security certification.
- GitHub Actions runs tests/fixtures on Python 3.10 and 3.12. Official `skills-ref` validator: **NOT_RUN** unless independently recorded.

See [rules](references/REFERENCE.md), [primary sources](references/SOURCES.md) and [MIT LICENSE](LICENSE). **Brand exception:** official Area Zero marks are excluded from the MIT software grant and must not be reused to imply endorsement.
