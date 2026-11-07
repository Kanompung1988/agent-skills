<p align="center"><img src="assets/areazero-logo.svg" alt="AREA ZERO — AI SOFTWARE HOUSE" width="280"></p>

# Kubernetes securityContext Audit

<p align="center"><strong>Small surface. Inspectable source. Honest security boundaries.</strong></p>

![CI](https://github.com/Kanompung1988/k8s-securitycontext-audit/actions/workflows/ci.yml/badge.svg) · MIT · Python 3.10–3.12

## Why this exists

Security settings can be inherited from Pod-level defaults or overridden per container. A superficial grep often misses effective settings or confuses optional hardening with formal Pod Security Standards requirements.

**What it does:** Review rendered Kubernetes Pod and workload securityContext effective settings, capabilities, seccomp, non-root defaults and host namespace hazards. Use before deployment or when reviewing Kubernetes YAML; never requires cluster credentials.

## Quick start (no credentials or outbound calls)

```bash
git clone https://github.com/Kanompung1988/k8s-securitycontext-audit.git
cd k8s-securitycontext-audit
python -m pip install 'PyYAML>=6.0,<7'
python scripts/audit.py examples/safe.yaml --json
```

For a flagged example: `python scripts/audit.py examples/review.yaml --json`.

| Exit | Meaning |
|:--|:--|
| `0` | No findings in the supplied input |
| `1` | One or more review findings |
| `2` | Invalid file, Git repository or input |

## Install as an Agent Skill

**Claude Code:** copy the *entire* repository as a named skill directory to `~/.claude/skills/k8s-securitycontext-audit/`; the root `SKILL.md` must be at `~/.claude/skills/k8s-securitycontext-audit/SKILL.md`. Restart/reload skill discovery as needed.

**Codex:** copy the *entire* repository to `~/.agents/skills/k8s-securitycontext-audit/` with `SKILL.md` at the root. Restart/reload skill discovery as needed. See [Agent Skills specification](https://agentskills.io/specification).

Use the skill when reviewing relevant input; don't activate it for unrelated tasks. The skill instructions deliberately prohibit execution of untrusted code or automatic modification of production systems.

## Tests / reproducibility

```bash
python -m pip install 'PyYAML>=6.0,<7'
python -m unittest discover -s tests -v
python scripts/audit.py examples/safe.yaml --json
```

CI runs Python 3.10 and 3.12, unit tests and a smoke invocation. **Official `skills-ref` validator: NOT_RUN** unless separately verified. Source fixtures are synthetic; no production security guarantees and no external review claimed. See [technical boundaries](references/REFERENCE.md).

## Design choices

- Offline, read-only local inspection; no cloud credentials.
- Deterministic JSON with stable rule identifiers.
- Review flags are explainable, non-mutating and not a substitute for effective runtime-policy evaluation.
- Pull requests and issues welcome; please include a minimal sanitized reproducer.

## License

MIT — see [LICENSE](LICENSE). Original Area Zero logo preserved unchanged from the established AREAZERO Skill Lab asset.
