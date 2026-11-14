<p align="center"><img src="assets/areazero-logo.svg" width="220" alt="Original AREAZERO identity"></p>
<p align="center"><img src="assets/hero.svg" width="100%" alt="npm release identity, OIDC and provenance audit"></p>

# npm Trusted Publisher Audit

**Review npm publishing trust boundaries before a release.** An offline Agent Skill that inspects GitHub Actions publishing jobs, effective OIDC permissions, hosted runners, local publisher inventory, token fallback, and provenance suppression. Deterministic rule IDs and machine-readable JSON.

## Installation and demo

~~~bash
git clone https://github.com/Kanompung1988/npm-trusted-publisher-audit.git
cd npm-trusted-publisher-audit
python -m pip install -r requirements.txt
python scripts/audit.py examples/safe --json
python scripts/audit.py examples/review --json    # expected exit 1
python -m unittest discover -s tests -v
~~~

**Claude Code:** clone this complete repository inside .claude/skills/npm-trusted-publisher-audit.
**Codex:** clone it inside .agents/skills/npm-trusted-publisher-audit.
Then instruct the agent to follow SKILL.md and audit a selected local project.

**Input:** project directory with package.json and .github/workflows YAML. Optional manually checked trusted-publisher.json with repository and workflow strings; never assume it is live registry truth.

## Safety and constraints

Read-only, no npm invocation, no GitHub or npm API, no secret-value reporting. Exit codes: 0 clean for supported heuristics, 1 findings, 2 invalid input. Only directly visible npm publish or npm stage publish run commands are analyzed; third-party actions, scripts and dynamic conditions may evade detection.

[Rule explanations](references/REFERENCE.md) · [Primary sources](references/SOURCES.md) · [MIT code license](LICENSE). Original AREAZERO artwork is a separate trademark and not covered by the code license. Report bugs with synthetic fixtures.
