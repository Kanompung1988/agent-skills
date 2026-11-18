#!/usr/bin/env python3
"""Read-only local caller/callee reusable-workflow contract review."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml

MAX_BYTES = 1_000_000
CALL_PREFIX = './.github/workflows/'


def load(path):
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('workflow file exceeds 1 MB limit')
    # YAML BaseLoader preserves GitHub's `on` key (YAML 1.1 normally converts it to True).
    data = yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
    if not isinstance(data, dict):
        raise ValueError('expected a YAML mapping')
    return data


def mapping(value):
    return value if isinstance(value, dict) else {}


def findings(workflow_dir):
    root = workflow_dir.resolve()
    if not root.is_dir():
        raise ValueError(f'no workflow directory: {root}')
    files = sorted(set(root.glob('*.yml')) | set(root.glob('*.yaml')))
    documents, results = {}, []

    def emit(code, severity, name, job, message):
        results.append(dict(code=code, severity=severity, file=name, job=job, message=message))

    for file in files:
        try:
            documents[file.name] = load(file)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            emit('INVALID_YAML', 'error', file.name, '-', str(exc))

    for name, doc in sorted(documents.items()):
        for job_id, job in mapping(doc.get('jobs')).items():
            if not isinstance(job, dict):
                continue
            used = job.get('uses')
            if not isinstance(used, str) or not used.startswith('./'):
                continue
            if not used.startswith(CALL_PREFIX):
                emit('UNSUPPORTED_LOCAL_PATH', 'review', name, job_id, 'local workflow reference is outside .github/workflows')
                continue
            dest = used[len(CALL_PREFIX):]
            if '/' in dest or '\\' in dest or dest in ('', '.', '..') or not dest.endswith(('.yaml', '.yml')):
                emit('UNSAFE_CALLEE_PATH', 'error', name, job_id, 'local callee path must be a direct workflow filename')
                continue
            if dest not in documents:
                emit('MISSING_CALLEE', 'review', name, job_id, f'{dest} unavailable or invalid in supplied directory')
                continue
            target = mapping(mapping(documents[dest].get('on')).get('workflow_call'))
            if not target and 'workflow_call' not in mapping(documents[dest].get('on')):
                emit('NOT_REUSABLE', 'error', name, job_id, f'{dest} does not define on.workflow_call')
                continue
            ins = mapping(target.get('inputs'))
            supplied = mapping(job.get('with'))
            for key, spec in ins.items():
                spec = mapping(spec)
                required = str(spec.get('required', 'false')).lower() == 'true'
                # A declared default satisfies the caller contract even when required is accidentally set.
                if required and key not in supplied and 'default' not in spec:
                    emit('MISSING_INPUT', 'error', name, job_id, f'required input {key!r} not provided to {dest}')
            for key, val in supplied.items():
                if key not in ins:
                    emit('UNKNOWN_INPUT', 'error', name, job_id, f'input {key!r} is not declared by {dest}')
                    continue
                typ = str(mapping(ins[key]).get('type','string'))
                if not isinstance(val, str) or '${{' in val:
                    continue
                if typ == 'boolean' and val.lower() not in ('true','false'):
                    emit('INPUT_TYPE', 'error', name, job_id, f'input {key!r} expects boolean literal')
                elif typ == 'number' and not re.fullmatch(r'-?(?:\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?', val):
                    emit('INPUT_TYPE', 'error', name, job_id, f'input {key!r} expects number literal')
            expected_secrets = mapping(target.get('secrets'))
            secrets = job.get('secrets')
            if secrets == 'inherit':
                continue  # Cannot know repository/organization secret availability offline.
            given = mapping(secrets)
            for key, spec in expected_secrets.items():
                if str(mapping(spec).get('required','false')).lower() == 'true' and key not in given:
                    emit('MISSING_SECRET', 'error', name, job_id, f'required secret {key!r} not passed to {dest}')
            for key in given:
                if key not in expected_secrets:
                    emit('UNKNOWN_SECRET', 'review', name, job_id, f'secret {key!r} not declared by {dest}')
    return sorted(results, key=lambda f:(f['file'],f['job'],f['code'],f['message']))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('workflows',type=Path,help='path to .github/workflows')
    p.add_argument('--json',action='store_true',dest='as_json')
    p.add_argument('--fail-on', choices=('error','review','never'), default='error')
    args=p.parse_args(argv)
    try: found=findings(args.workflows)
    except (ValueError,OSError) as exc:
        print(f'input error: {exc}',file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps({'findings':found,'counts':{'error':sum(f['severity']=='error' for f in found),'review':sum(f['severity']=='review' for f in found)}},indent=2))
    else:
        for f in found:
            print(f"{f['file']} [{f['job']}] {f['severity'].upper()} {f['code']}: {f['message']}")
        print(f'{len(found)} finding(s)')
    if args.fail_on=='never': return 0
    return 2 if any(f['severity']=='error' or args.fail_on=='review' for f in found) else 0

if __name__=='__main__':
    sys.exit(main())
