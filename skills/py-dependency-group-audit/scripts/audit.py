#!/usr/bin/env python3
"""Read-only PEP 735 dependency-group contract checker. Never resolves or installs deps."""
import argparse
import json
import re
import sys
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from packaging.requirements import Requirement, InvalidRequirement


def normalize(value):
    return re.sub(r'[-_.]+', '-', value).lower()


def audit(data):
    findings = []
    groups = data.get('dependency-groups', {})
    def add(code, group, detail, severity='review'):
        findings.append(dict(code=code, group=group, severity=severity, detail=detail))
    if not isinstance(groups, dict):
        add('GROUPS_NOT_TABLE', '-', 'dependency-groups must be a TOML table', 'error')
        return findings
    names = {}
    for name in groups:
        norm = normalize(name)
        if norm in names:
            add('NAME_COLLISION', name, 'Normalized name collides with ' + names[norm], 'error')
        else:
            names[norm] = name
    edges = {name: [] for name in groups}
    for name, entries in groups.items():
        if not isinstance(entries, list):
            add('GROUP_NOT_LIST', name, 'Group value must be a list', 'error')
            continue
        for i, entry in enumerate(entries):
            if isinstance(entry, str):
                try:
                    Requirement(entry)
                except InvalidRequirement:
                    add('INVALID_REQUIREMENT', name, f'Entry {i} is not a PEP 508 requirement', 'error')
            elif isinstance(entry, dict):
                if set(entry) != {'include-group'} or not isinstance(entry.get('include-group'), str):
                    add('INVALID_INCLUDE', name, f'Entry {i} must contain only a string include-group', 'error')
                    continue
                target = names.get(normalize(entry['include-group']))
                if target is None:
                    add('UNKNOWN_GROUP', name, f'Entry {i} refers to an undeclared group', 'error')
                else:
                    edges[name].append(target)
            else:
                add('INVALID_ENTRY', name, f'Entry {i} is not a string or include object', 'error')
    colors = {}
    seen = set()
    def visit(name, trail):
        if colors.get(name) == 1:
            cycle = trail[trail.index(name):] + [name]
            signature = tuple(sorted(set(cycle)))
            if signature not in seen:
                seen.add(signature)
                add('INCLUDE_CYCLE', name, ' -> '.join(cycle), 'error')
            return
        if colors.get(name) == 2:
            return
        colors[name] = 1
        for other in edges[name]:
            visit(other, trail + [other])
        colors[name] = 2
    for name in groups:
        if not colors.get(name):
            visit(name, [name])
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pyproject', type=Path)
    parser.add_argument('--json', action='store_true', help='Machine-readable findings')
    args = parser.parse_args(argv)
    try:
        if args.pyproject.stat().st_size > 2_000_000:
            raise ValueError('input exceeds 2 MB limit')
        with args.pyproject.open('rb') as stream:
            data = tomllib.load(stream)
        result = audit(data)
    except (OSError, ValueError, tomllib.TOMLDecodeError):
        print('Unable to inspect input (I/O, size or TOML parse error)', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({'findings': result, 'count': len(result)}, indent=2))
    else:
        for item in result:
            print(f"[{item['severity']}] {item['code']} ({item['group']}): {item['detail']}")
        print(f'{len(result)} finding(s)')
    return 1 if result else 0


if __name__ == '__main__':
    sys.exit(main())
