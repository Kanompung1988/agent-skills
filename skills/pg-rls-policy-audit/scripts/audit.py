#!/usr/bin/env python3
"""Conservative offline PostgreSQL RLS DDL review; never connect to a database."""
import argparse
import json
import re
import sys
from pathlib import Path

IDENT = r'(?:(?:"(?:[^"]|"")*"|[a-zA-Z_][a-zA-Z_0-9$]*)(?:\s*\.\s*(?:"(?:[^"]|"")*"|[a-zA-Z_][a-zA-Z_0-9$]*))?)'
ALTER = re.compile(r'^\s*ALTER\s+TABLE\s+(?:ONLY\s+)?(' + IDENT + r')\s+(ENABLE|DISABLE|FORCE|NO\s+FORCE)\s+ROW\s+LEVEL\s+SECURITY\b', re.I | re.S)
POLICY = re.compile(r'^\s*CREATE\s+POLICY\s+(' + IDENT + r')\s+ON\s+(' + IDENT + r')(?=\s|$)', re.I | re.S)


def statements(sql):
    """Split SQL on real semicolons, masking comments/string literals only."""
    out, start, i, length, state, tag, depth = [], 0, 0, len(sql), 'normal', '', 0
    masked = list(sql)
    while i < length:
        ch = sql[i]
        if state == 'normal':
            if sql.startswith('--', i):
                state = 'line'; masked[i:i+2] = '  '; i += 2; continue
            if sql.startswith('/*', i):
                state = 'block'; depth = 1; masked[i:i+2] = '  '; i += 2; continue
            if ch == "'":
                state = 'string'; masked[i] = ' '; i += 1; continue
            if ch == '"':
                state = 'ident'; i += 1; continue
            if ch == '$':
                m = re.match(r'\$[A-Za-z_0-9]*\$', sql[i:])
                if m:
                    tag = m.group(); state='dollar'; masked[i:i+len(tag)] = ' '*len(tag); i += len(tag); continue
            if ch == ';':
                out.append((''.join(masked[start:i]), sql.count('\n', 0, start)+1))
                start = i + 1
        elif state == 'ident':
            if ch == '"':
                if i+1 < length and sql[i+1] == '"': i += 2; continue
                state = 'normal'
        elif state == 'line':
            if ch == '\n': state = 'normal'
            else: masked[i] = ' '
        elif state == 'block':
            if sql.startswith('/*', i): depth += 1; masked[i:i+2]='  '; i += 2; continue
            if sql.startswith('*/', i):
                depth -= 1; masked[i:i+2]='  '; i += 2
                if depth == 0: state = 'normal'
                continue
            masked[i] = '\n' if ch == '\n' else ' '
        elif state == 'string':
            if ch == "'":
                if i+1 < length and sql[i+1] == "'": masked[i:i+2]='  '; i += 2; continue
                state = 'normal'
            masked[i] = '\n' if ch == '\n' else ' '
        elif state == 'dollar':
            if sql.startswith(tag, i):
                masked[i:i+len(tag)] = ' '*len(tag); i += len(tag); state = 'normal'; continue
            masked[i] = '\n' if ch == '\n' else ' '
        i += 1
    if ''.join(masked[start:]).strip():
        out.append((''.join(masked[start:]), sql.count('\n', 0, start)+1))
    return out


def canonical(identifier):
    parts = re.findall(r'"(?:[^"]|"")*"|[A-Za-z_][\w$]*', identifier)
    return '.'.join(p[1:-1].replace('""','"') if p.startswith('"') else p.lower() for p in parts)


def audit(sql):
    state, findings = {}, []
    def add(code, table, line, text, severity='review'):
        findings.append({'code':code,'table':table,'line':line,'severity':severity,'detail':text})
    for stmt, line in statements(sql):
        m = ALTER.search(stmt)
        if m:
            table, mode = canonical(m.group(1)), ' '.join(m.group(2).upper().split())
            entry = state.setdefault(table, {'enabled':None,'force':None,'policies':[], 'line':line})
            if mode == 'ENABLE': entry['enabled'] = True
            if mode == 'DISABLE':
                entry['enabled'] = False
                add('RLS_DISABLED', table, line, 'DDL disables row security', 'high')
            if mode == 'FORCE': entry['force'] = True
            if mode == 'NO FORCE': entry['force'] = False
            continue
        m = POLICY.search(stmt)
        if m:
            table = canonical(m.group(2))
            entry = state.setdefault(table, {'enabled':None,'force':None,'policies':[], 'line':line})
            entry['policies'].append(line)
            rest = stmt[m.end():]
            if re.search(r'\bTO\s+PUBLIC\b', rest, re.I):
                add('PUBLIC_POLICY', table, line, 'Policy targets PUBLIC (review intended scope)')
            if re.search(r'\bUSING\s*\(\s*TRUE\s*\)', rest, re.I):
                add('UNRESTRICTED_USING', table, line, 'Literal USING (true) admits all rows for matching roles')
            if re.search(r'\bWITH\s+CHECK\s*\(\s*TRUE\s*\)', rest, re.I):
                add('UNRESTRICTED_CHECK', table, line, 'Literal WITH CHECK (true) admits all candidate rows')
            continue
    for table, entry in state.items():
        if entry['policies'] and entry['enabled'] is None:
            add('ENABLE_NOT_SHOWN', table, entry['policies'][0], 'No ENABLE ROW LEVEL SECURITY appears in supplied SQL')
        if entry['enabled'] and entry['force'] is not True:
            add('OWNER_BYPASS_REVIEW', table, entry['line'], 'Owner normally bypasses RLS unless FORCE is set')
        if entry['enabled'] and not entry['policies']:
            add('NO_POLICY_IN_INPUT', table, entry['line'], 'No policy in supplied SQL; PostgreSQL defaults to deny (other migrations may supply one)', 'info')
    return sorted(findings, key=lambda f:(f['line'],f['code']))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sql_file', type=Path)
    p.add_argument('--json', action='store_true')
    args = p.parse_args(argv)
    try:
        if args.sql_file.stat().st_size > 2_000_000:
            raise ValueError('file too large')
        data = args.sql_file.read_text(encoding='utf8')
    except (OSError, UnicodeError, ValueError) as e:
        print('Unable to inspect input: '+type(e).__name__,file=sys.stderr)
        return 2
    findings = audit(data)
    if args.json:
        print(json.dumps({'count':len(findings),'findings':findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['line']} [{f['severity']}] {f['code']} {f['table']}: {f['detail']}")
        print(f'{len(findings)} finding(s)')
    return 1 if findings else 0

if __name__ == '__main__': sys.exit(main())
