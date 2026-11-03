#!/usr/bin/env python3
"""Audit pip requirements index trust boundaries without installing packages."""
import argparse
import json
from pathlib import Path
import re
import shlex
import sys
from urllib.parse import urlsplit

MAX_BYTES = 1_000_000
MAX_DEPTH = 8

def emit(out, code, severity, file, line, message):
    out.append({'code': code, 'severity': severity, 'file': file, 'line': line, 'message': message})

def _tokens(line):
    try:
        return shlex.split(line, comments=True, posix=True)
    except ValueError:
        return None

def audit(root, entry):
    root = root.resolve()
    found, visited = [], set()
    state = {'indexes': [], 'extra': [], 'noindex': False}

    def visit(path, depth):
        try:
            candidate = path.resolve(strict=True)
            rel = candidate.relative_to(root)
        except (OSError, ValueError):
            emit(found, 'OUTSIDE_ROOT', 'error', '<include>', 0, 'included file absent or outside allowed root')
            return
        if depth > MAX_DEPTH:
            emit(found, 'INCLUDE_DEPTH', 'error', str(rel), 0, 'include exceeds maximum depth 8')
            return
        if candidate in visited:
            return
        visited.add(candidate)
        try:
            if candidate.stat().st_size > MAX_BYTES:
                raise ValueError('file too large')
            lines = candidate.read_text(encoding='utf-8').splitlines()
        except (OSError, UnicodeError, ValueError):
            emit(found, 'UNREADABLE', 'error', str(rel), 0, 'file unreadable or exceeds 1 MB')
            return
        for no, raw in enumerate(lines, 1):
            stripped = raw.strip()
            if not stripped or stripped.startswith('#'):
                continue
            words = _tokens(stripped)
            if words is None:
                emit(found, 'INVALID_SHELL_QUOTING', 'warning', str(rel), no, 'cannot parse requirements line')
                continue
            if not words:
                continue
            option = words[0]
            # Pip permits both --name=value and --name value. Do not echo values.
            flag = option.split('=', 1)[0]
            short = option[:2]
            if flag in ('-r', '--requirement', '-c', '--constraint') or short in ('-r', '-c'):
                value = (option[2:] if short in ('-r', '-c') and len(option) > 2 else
                         option.split('=', 1)[1] if '=' in option else words[1] if len(words) > 1 else None)
                if not value or value.startswith('-'):
                    emit(found, 'INVALID_INCLUDE', 'error', str(rel), no, 'missing include path')
                else:
                    visit(candidate.parent / value, depth + 1)
                continue
            if flag in ('--extra-index-url',) or option.startswith('--extra-index-url='):
                state['extra'].append((str(rel), no))
                emit(found, 'EXTRA_INDEX', 'warning', str(rel), no, 'additional index may allow dependency confusion; review package origin policy')
            if flag in ('--index-url', '-i') or option.startswith('--index-url='):
                state['indexes'].append((str(rel), no))
            if flag in ('--no-index',):
                state['noindex'] = True
            if flag in ('--trusted-host',):
                emit(found, 'TRUSTED_HOST', 'warning', str(rel), no, 'trusted-host weakens TLS trust checks')
            if flag in ('--index-url', '--extra-index-url', '-i') or option.startswith(('--index-url=', '--extra-index-url=')):
                value = option.split('=', 1)[1] if '=' in option else words[1] if len(words) > 1 else ''
                if value:
                    parsed = urlsplit(value)
                    if parsed.scheme.lower() == 'http':
                        emit(found, 'PLAIN_HTTP_INDEX', 'warning', str(rel), no, 'package index uses plaintext HTTP')
                    elif parsed.scheme.lower() not in ('https', 'file'):
                        emit(found, 'UNKNOWN_INDEX_SCHEME', 'warning', str(rel), no, 'index URL scheme not recognized')
    visit(entry, 0)
    if state['extra'] and state['indexes'] and not state['noindex']:
        f, n = state['extra'][0]
        emit(found, 'MULTI_INDEX', 'info', f, n, 'pip index resolution is not a repository-priority system')
    return sorted(found, key=lambda x: (x['file'], x['line'], x['code']))

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('requirements', type=Path)
    p.add_argument('--root', type=Path, help='allowed root for nested -r/-c includes (default: parent of entry)')
    p.add_argument('--format', choices=['json', 'text'], default='text')
    a = p.parse_args(argv)
    root = a.root or a.requirements.parent
    try:
        results = audit(root, a.requirements)
    except (OSError, ValueError):
        print('ERROR: invalid requirements path', file=sys.stderr)
        return 2
    if a.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        for f in results:
            print(f'{f["severity"]:7} {f["code"]:21} {f["file"]}:{f["line"]} — {f["message"]}')
        if not results:
            print('No configured index warnings found; environment/pip.conf/dependency sources not inspected.')
    return 1 if any(f['severity'] in ('error', 'warning') for f in results) else 0

if __name__ == '__main__':
    raise SystemExit(main())
