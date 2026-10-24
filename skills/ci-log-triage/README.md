# ci-log-triage

Turn noisy build logs into an offline, redacted evidence map for agent-assisted debugging. This script **does not infer definitive root causes** or fix code; it points engineers to reproducible evidence.

## Quick start

Requires Python 3.10+ (stdlib only).

```bash
python3 scripts/triage_ci.py --input ./ci.log --format markdown
python3 scripts/triage_ci.py --input ./ci.log --format json --out /tmp/report.json
```

Reports include grouped failure classes, confidence *hints*, count, line-numbered redacted evidence and safe next verification steps. Signals cover TypeScript, pytest/Jest, import errors, disk/memory, Docker, dependency resolution, permissions, auth, network and timeouts. A "high" label means the pattern is recognizable, not that causation is proven.

## Safety

No network calls; no commands are executed from the input. API keys, bearer tokens, selected GitHub/GitLab/OpenAI token prefixes and key-value credentials are masked using heuristics. **Sanitization is not comprehensive**: inspect snippets before sharing publicly. Do not put sensitive raw logs in public tools.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT, see this folder's LICENSE and repository LICENSE. No borrowed proprietary regex rule sets.
