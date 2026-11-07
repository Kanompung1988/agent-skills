<p align="center"><img src="assets/areazero-logo.svg" alt="AREA ZERO — AI SOFTWARE HOUSE" width="280"></p>

# Git Submodule Boundary Audit

<p align="center"><strong>Small surface. Inspectable source. Honest security boundaries.</strong></p>

![CI](https://github.com/Kanompung1988/git-submodule-boundary-audit/actions/workflows/ci.yml/badge.svg) · MIT · Python 3.10–3.12

## Why this exists

Git pins a submodule to a commit in the index, while .gitmodules declares where Git may fetch it and whether a remote branch should be followed with --remote. Reviewers can miss unsafe URLs, orphaned gitlinks and misleading branch settings.

**What it does:** Audit local Git submodule .gitmodules declarations against staged index gitlinks and flag unsafe source URLs or update tracking. Use when reviewing a repository with submodules or before merging changes to .gitmodules; never fetches or executes submodule code.

## Quick start (no credentials or outbound calls)

```bash
git clone https://github.com/Kanompung1988/git-submodule-boundary-audit.git
cd git-submodule-boundary-audit
git --version
python scripts/audit.py . --json
```

For a realistic check, run `python scripts/audit.py /path/to/your/repo --json` (reads the staged index; no fetch). Tests construct synthetic local repositories.

| Exit | Meaning |
|:--|:--|
| `0` | No findings in the supplied input |
| `1` | One or more review findings |
| `2` | Invalid file, Git repository or input |

## Install as an Agent Skill

**Claude Code:** copy the *entire* repository as a named skill directory to `~/.claude/skills/git-submodule-boundary-audit/`; the root `SKILL.md` must be at `~/.claude/skills/git-submodule-boundary-audit/SKILL.md`. Restart/reload skill discovery as needed.

**Codex:** copy the *entire* repository to `~/.agents/skills/git-submodule-boundary-audit/` with `SKILL.md` at the root. Restart/reload skill discovery as needed. See [Agent Skills specification](https://agentskills.io/specification).

Use the skill when reviewing relevant input; don't activate it for unrelated tasks. The skill instructions deliberately prohibit execution of untrusted code or automatic modification of production systems.

## Tests / reproducibility

```bash
python -m unittest discover -s tests -v
python scripts/audit.py . --json
```

CI runs Python 3.10 and 3.12, unit tests and a smoke invocation. **Official `skills-ref` validator: NOT_RUN** unless separately verified. Source fixtures are synthetic; no production security guarantees and no external review claimed. See [technical boundaries](references/REFERENCE.md).

## Design choices

- Offline, read-only local inspection; no cloud credentials.
- Deterministic JSON with stable rule identifiers.
- Review flags are explainable, non-mutating and not a substitute for effective runtime-policy evaluation.
- Pull requests and issues welcome; please include a minimal sanitized reproducer.

## License

MIT — see [LICENSE](LICENSE). Original Area Zero logo preserved unchanged from the established AREAZERO Skill Lab asset.
