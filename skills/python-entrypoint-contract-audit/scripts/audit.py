#!/usr/bin/env python3
"""Offline audit of PEP 621 Python CLI entry-point declarations and local targets."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

MAX_BYTES = 1_000_000
# Object references follow the PyPA entry-points specification, with optional extras.
REFERENCE = re.compile(r"^\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*:\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(?:\s*\[\s*([A-Za-z0-9_,\s-]+)\s*\])?\s*$", re.ASCII)
SCRIPT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$", re.ASCII)


def finding(code: str, severity: str, script: str, detail: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "script": script, "detail": detail}


def module_exists(root: Path, module: str) -> bool:
    rel = Path(*module.split('.'))
    # No arbitrary package imports or execution: purely file existence checks.
    for base in (root / 'src', root):
        if (base / rel).with_suffix('.py').is_file() or (base / rel / '__init__.py').is_file():
            return True
    return False


def evaluate(document: Any, root: Path, targets: bool = True) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(document, dict) or not isinstance(document.get('project'), dict):
        return [finding('INVALID_PROJECT', 'error', '-', 'pyproject.toml requires a [project] table for static auditing')]
    project = document['project']
    dynamic = project.get('dynamic', [])
    if not isinstance(dynamic, list):
        out.append(finding('INVALID_DYNAMIC', 'error', '-', 'project.dynamic must be a list'))
        dynamic = []
    ep = project.get('entry-points', {})
    if not isinstance(ep, dict):
        out.append(finding('INVALID_ENTRY_POINTS', 'error', '-', 'project.entry-points must be a table'))
        ep = {}
    for reserved in ('console_scripts', 'gui_scripts'):
        if reserved in ep:
            out.append(finding('RESERVED_ENTRY_POINT_GROUP', 'error', reserved,
                               f'Use [project.scripts] / [project.gui-scripts], never [project.entry-points.{reserved}]'))
    collected = []
    for group in ('scripts', 'gui-scripts'):
        table = project.get(group, {})
        if group in dynamic and group not in project:
            out.append(finding('DYNAMIC_GROUP', 'info', group, 'Backend generates metadata; static declarations unavailable'))
        if not isinstance(table, dict):
            out.append(finding('INVALID_GROUP', 'error', group, f'project.{group} must be a table'))
            continue
        if group in dynamic and group in project:
            out.append(finding('DYNAMIC_STATIC_CONFLICT', 'error', group, f'project.{group} is both static and dynamic'))
        for name, value in table.items():
            label = str(name)
            collected.append((group, label, value))
    scripts = {name for group, name, _ in collected if group == 'scripts'}
    for group, name, value in collected:
        if group == 'gui-scripts' and name in scripts:
            out.append(finding('DUPLICATE_COMMAND', 'error', name, 'Command name declared in scripts and gui-scripts'))
        if not SCRIPT_NAME.fullmatch(name):
            out.append(finding('INVALID_NAME', 'error', name, 'Script name must be alphanumeric, dot, underscore or hyphen'))
        if not isinstance(value, str):
            out.append(finding('INVALID_REFERENCE', 'error', name, 'Entry-point reference must be a string'))
            continue
        match = REFERENCE.fullmatch(value)
        if not match:
            out.append(finding('INVALID_REFERENCE', 'error', name, 'Expected module.path:callable.qualname (optional [extras])'))
            continue
        module, obj, extras = match.groups()
        if extras:
            out.append(finding('DEPRECATED_EXTRAS', 'review', name, 'Entrypoint extras are discouraged by PyPA; check installation compatibility'))
        if targets and not module_exists(root, module):
            out.append(finding('MODULE_NOT_FOUND_LOCALLY', 'review', name, f'{module} missing from root/ or src/; can be generated or provided by dependency'))
        if obj.startswith('_'):
            out.append(finding('PRIVATE_TARGET', 'review', name, 'Entrypoint targets a private object; confirm stable public API'))
    return sorted(out, key=lambda r: (r['script'], r['code'], r['detail']))


def audit(pyproject: Path, targets: bool = True) -> list[dict[str, str]]:
    if not pyproject.is_file() or pyproject.stat().st_size > MAX_BYTES:
        raise ValueError('Input must be a local pyproject.toml <= 1MB')
    with pyproject.open('rb') as stream:
        obj = tomllib.load(stream)
    return evaluate(obj, pyproject.parent, targets)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pyproject', type=Path, help='Local pyproject.toml')
    p.add_argument('--no-target-check', action='store_true', help='Skip local src/root module existence heuristics')
    p.add_argument('--format', choices=['json', 'text'], default='text')
    p.add_argument('--strict', action='store_true', help='Fail with exit 1 on error-severity findings')
    args = p.parse_args(argv)
    try:
        findings = audit(args.pyproject, not args.no_target_check)
    except (OSError, ValueError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 2
    if args.format == 'json':
        print(json.dumps({'findings': findings, 'count': len(findings)}, indent=2))
    else:
        for f in findings:
            print(f"{f['severity'].upper():6} {f['code']}: {f['script']} — {f['detail']}")
        print(f'{len(findings)} finding(s)')
    return 1 if args.strict and any(f['severity'] == 'error' for f in findings) else 0


if __name__ == '__main__':
    raise SystemExit(main())
