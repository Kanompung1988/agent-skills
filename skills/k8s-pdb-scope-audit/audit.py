#!/usr/bin/env python3
"""Read-only PodDisruptionBudget selector audit (not an eviction simulator)."""
import argparse
import json
from pathlib import Path
import sys
import yaml

MAX_BYTES = 2_000_000

def labels_match(selector, labels):
    """Return True/False/None; None means unsupported/invalid selector."""
    if not isinstance(selector, dict) or not isinstance(labels, dict):
        return None
    if not set(selector).issubset({'matchLabels', 'matchExpressions'}):
        return None
    ml = selector.get('matchLabels', {})
    ex = selector.get('matchExpressions', [])
    if not isinstance(ml, dict) or not isinstance(ex, list):
        return None
    for key, val in ml.items():
        if not isinstance(key, str) or not isinstance(val, str):
            return None
        if labels.get(key) != val:
            return False
    for term in ex:
        if not isinstance(term, dict) or not isinstance(term.get('key'), str):
            return None
        key, op, vals = term['key'], term.get('operator'), term.get('values', [])
        if op in ('In', 'NotIn'):
            if not isinstance(vals, list) or not vals or any(not isinstance(v, str) for v in vals):
                return None
            if op == 'In' and labels.get(key) not in vals:
                return False
            if op == 'NotIn' and (key not in labels or labels[key] in vals):
                return False
        elif op == 'Exists':
            if key not in labels:
                return False
        elif op == 'DoesNotExist':
            if key in labels:
                return False
        else:
            return None
    return True

def emit(out, code, level, origin, detail):
    out.append({'code': code, 'severity': level, 'object': origin, 'message': detail})

def check_budget(doc, pods, seen, out):
    api = doc.get('apiVersion')
    meta = doc.get('metadata', {})
    spec = doc.get('spec', {})
    if not isinstance(meta, dict) or not isinstance(spec, dict):
        emit(out, 'INVALID_OBJECT', 'error', 'unknown', 'metadata/spec must be objects')
        return
    name = str(meta.get('name', 'unnamed'))
    ns = str(meta.get('namespace') or 'default')
    ident = f'{ns}/{name}'
    if api != 'policy/v1':
        emit(out, 'API_VERSION', 'warning', ident, 'expected policy/v1 PodDisruptionBudget')
    has_min, has_max = 'minAvailable' in spec, 'maxUnavailable' in spec
    if has_min == has_max:
        emit(out, 'BUDGET_FIELDS', 'error', ident, 'exactly one of minAvailable / maxUnavailable is required')
    for fld in ('minAvailable', 'maxUnavailable'):
        if fld in spec:
            v = spec[fld]
            if isinstance(v, bool) or (not isinstance(v, (int, str))):
                emit(out, 'INVALID_BUDGET', 'error', ident, f'{fld} must be a nonnegative integer or percentage')
            elif isinstance(v, int) and v < 0:
                emit(out, 'INVALID_BUDGET', 'error', ident, f'{fld} must not be negative')
            elif isinstance(v, str) and (not v.endswith('%') or not v[:-1].isdigit() or int(v[:-1]) > 100):
                emit(out, 'INVALID_BUDGET', 'error', ident, f'{fld} invalid percentage')
    if spec.get('maxUnavailable') in (0, '0%') or spec.get('minAvailable') == '100%':
        emit(out, 'ZERO_DISRUPTIONS', 'info', ident, 'may block voluntary evictions; verify workload availability')
    if 'selector' not in spec or spec.get('selector') is None:
        emit(out, 'NULL_SELECTOR', 'warning', ident, 'selector matches no pods')
        return
    sel = spec['selector']
    if not isinstance(sel, dict):
        emit(out, 'INVALID_SELECTOR', 'error', ident, 'selector must be an object')
        return
    if sel == {} or sel == {'matchLabels': {}} or sel == {'matchExpressions': []}:
        emit(out, 'ALL_PODS', 'warning', ident, 'policy/v1 empty selector matches every pod in namespace')
    found = []
    for pod in pods:
        if pod['namespace'] != ns:
            continue
        matches = labels_match(sel, pod['labels'])
        if matches is None:
            emit(out, 'UNSUPPORTED_SELECTOR', 'warning', ident, 'selector could not be evaluated; cannot infer coverage')
            return
        if matches:
            found.append(pod['name'])
            key = (ns, pod['name'])
            if key in seen:
                emit(out, 'OVERLAP', 'warning', ident, f'pod {pod["name"]} also selected by {seen[key]}')
            else:
                seen[key] = ident
    if not found:
        emit(out, 'NO_PODS_IN_INPUT', 'info', ident, 'no matching Pod manifests in input; live cluster is unknown')

def audit(documents):
    docs = [d for d in documents if d is not None]
    out, pods, budgets = [], [], []
    for d in docs:
        if not isinstance(d, dict):
            emit(out, 'INVALID_DOCUMENT', 'error', 'unknown', 'document must be a mapping')
            continue
        if d.get('kind') == 'Pod':
            meta = d.get('metadata') or {}
            if isinstance(meta, dict):
                pods.append({'namespace': str(meta.get('namespace') or 'default'),
                             'name': str(meta.get('name') or 'unnamed'),
                             'labels': meta.get('labels') or {}})
        elif d.get('kind') == 'PodDisruptionBudget':
            budgets.append(d)
    seen = {}
    for d in budgets:
        check_budget(d, pods, seen, out)
    if not budgets:
        emit(out, 'NO_BUDGETS', 'info', 'input', 'no PodDisruptionBudget manifests found')
    return sorted(out, key=lambda e: (e['object'], e['code'], e['message']))

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifests', type=Path, help='YAML/JSON multi-document manifests; read only')
    p.add_argument('--format', choices=['json', 'text'], default='text')
    args = p.parse_args(argv)
    try:
        if args.manifests.stat().st_size > MAX_BYTES:
            raise ValueError('input exceeds 2 MB')
        docs = list(yaml.safe_load_all(args.manifests.read_text(encoding='utf-8')))
        report = audit(docs)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        print(f'ERROR: invalid input ({type(exc).__name__})', file=sys.stderr)
        return 2
    if args.format == 'json':
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for r in report:
            print(f'{r["severity"]:7} {r["code"]:21} {r["object"]} — {r["message"]}')
        if not report:
            print('No findings from available manifests (not proof of live availability).')
    return 1 if any(x['severity'] in ('error', 'warning') for x in report) else 0

if __name__ == '__main__':
    raise SystemExit(main())
