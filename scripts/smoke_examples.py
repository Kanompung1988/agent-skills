#!/usr/bin/env python3
"""Run the documented offline examples and assert known, deterministic results."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def command(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *parts], cwd=ROOT, text=True, capture_output=True, check=False, timeout=20)


def main() -> int:
    a = command('skills/openapi-compat-audit/scripts/compare_openapi.py', '--old',
                'examples/openapi-before.json', '--new', 'examples/openapi-after.json', '--format', 'json')
    if a.returncode != 2:
        raise AssertionError(f'OpenAPI example should exit 2 (breaking), got {a.returncode}: {a.stderr}')
    p = json.loads(a.stdout)
    if p['summary'] != {'breaking': 3, 'review': 0}:
        raise AssertionError(f'Unexpected OpenAPI findings: {p["summary"]!r}')
    b = command('skills/ci-log-triage/scripts/triage_ci.py', '--input',
                'examples/synthetic-ci.log', '--format', 'json')
    if b.returncode:
        raise AssertionError(f'CI triage example exited {b.returncode}: {b.stderr}')
    q = json.loads(b.stdout)
    assert q['summary']['signals'] == 3, q['summary']
    assert q['metadata']['inspected_lines'] == 9, q['metadata']
    expected = {'typescript', 'missing-dependency', 'test-assertion'}
    assert set(x['rule'] for x in q['findings']) == expected, q['findings']
    print('PASS: OpenAPI example (3 documented breaking findings, exit 2)')
    print('PASS: CI log sample (3 documented signals, 9 lines, exit 0)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
