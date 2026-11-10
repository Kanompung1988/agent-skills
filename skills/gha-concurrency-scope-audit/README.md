<p align="center"><img src="assets/areazero-logo.svg" alt="Original AREAZERO logo" width="210"></p>

# GitHub Actions Concurrency Scope Audit

**Review unexpected CI cancellations before they break releases.** This standalone read-only Agent Skill detects literal concurrency-group collisions, including case-insensitive duplicates across job and workflow scopes.

### Capabilities
CC001–CC007 cover missing groups, invalid queue combinations, release/deploy cancellation flags, default pending queue, and repository-wide collisions. JSON output includes `file`, `scope`, `code`, `message`, `files_scanned`, and unresolved dynamic group count.

### Run locally
```bash
git clone https://github.com/Kanompung1988/gha-concurrency-scope-audit.git
cd gha-concurrency-scope-audit
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe.yml --json     # exit 0
python scripts/audit.py examples/review.yml --json   # exit 1 (expected)
python -m unittest discover -s tests -v
```

### Install for agents
**Claude Code** (from your project): `git clone https://github.com/Kanompung1988/gha-concurrency-scope-audit.git .claude/skills/gha-concurrency-scope-audit`

**Codex** (from your project): `git clone https://github.com/Kanompung1988/gha-concurrency-scope-audit.git .agents/skills/gha-concurrency-scope-audit`

Use the installed Skill's `SKILL.md` to conduct scoped review; run `scripts/audit.py` from its root.

### Trust boundaries
Inputs are local workflow YAML only; no actions run, no GitHub network API calls, and no secrets needed. Dynamic expressions are left unresolved; equal groups may intentionally coordinate workflows. Use results to guide a review, not to claim GitHub queue state or security certification. Exit 0 clean, 1 findings, 2 errors. MIT License. See [rule definitions](references/REFERENCE.md) and [official sources](references/SOURCES.md).
