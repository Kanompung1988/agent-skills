<p align="center"><img src="assets/areazero-logo.svg" alt="Original AREAZERO logo" width="210"></p>

# BuildKit Secret Boundary Audit

**Keep build-time credentials out of image metadata.** A focused, offline Dockerfile review Agent Skill for Claude Code and Codex.

This read-only tool identifies sensitive-looking ARG/ENV names, optional BuildKit secret mounts, RUN variables without a mount, credential-like copied paths, and credential-bearing ADD URLs. It does not require Docker or any credentials.

### Quick start
```bash
git clone https://github.com/Kanompung1988/buildkit-secret-boundary-audit.git
cd buildkit-secret-boundary-audit
python scripts/audit.py examples/Dockerfile.safe --json     # exit 0
python scripts/audit.py examples/Dockerfile.review --json   # exit 1 (review expected)
python -m unittest discover -s tests -v
```

### Agent installation
**Claude Code:** `git clone https://github.com/Kanompung1988/buildkit-secret-boundary-audit.git .claude/skills/buildkit-secret-boundary-audit`

**Codex:** `git clone https://github.com/Kanompung1988/buildkit-secret-boundary-audit.git .agents/skills/buildkit-secret-boundary-audit`

Read `SKILL.md` and run `scripts/audit.py PATH --json` from the skill root. JSON includes codes, line numbers, static messages and error list; exit 0 clean, 1 findings, 2 invalid input.

### Trust boundaries
No build execution, file modification, daemon connection, registry access, or secret decoding. False positives are possible from variable-name patterns; not all unsafe paths can be detected. Actual invocation and layer content require separate checks. See [rule definitions](references/REFERENCE.md), [Docker primary sources](references/SOURCES.md) and MIT License.
