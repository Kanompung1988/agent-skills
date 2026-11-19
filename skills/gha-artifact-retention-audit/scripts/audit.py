#!/usr/bin/env python3
"""Read-only GitHub Actions upload-artifact retention policy reviewer."""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml


ACTION = re.compile(r'^actions/upload-artifact@[^\s]+$', re.IGNORECASE)


def finding(severity, code, location, message):
    return {"severity": severity, "code": code, "location": location, "message": message}


def retention_value(raw):
    """Return kind and integer, or a safe diagnostic category. 0 uses repository default."""
    if raw is None:
        return "default", None
    if isinstance(raw, bool):
        return "invalid", None
    if isinstance(raw, int):
        return "number", raw
    if isinstance(raw, str):
        if re.fullmatch(r'\s*\d+\s*', raw):
            return "number", int(raw.strip())
        if "${{" in raw or "$" in raw:
            return "dynamic", None
        return "invalid", None
    return "invalid", None


def analyze_doc(doc, label, *, visibility='unknown', policy_days=None, minimum_days=None):
    if not isinstance(doc, dict):
        raise ValueError("workflow must be a mapping")
    jobs = doc.get('jobs', {})
    if not isinstance(jobs, dict):
        raise ValueError("jobs must be a mapping")
    max_cap = {"public": 90, "private": 400, "unknown": 400}[visibility]
    findings = []
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        steps = job.get('steps', [])
        if not isinstance(steps, list):
            findings.append(finding('review', 'STEPS_UNRESOLVED', f'{label}:{job_name}', 'Job steps are not a list'))
            continue
        for i, step in enumerate(steps, 1):
            if not isinstance(step, dict):
                continue
            uses = step.get('uses')
            if not isinstance(uses, str) or not ACTION.fullmatch(uses.strip()):
                continue
            loc = f'{label}:{job_name}:steps[{i}]'
            with_clause = step.get('with', {})
            if with_clause is None:
                with_clause = {}
            if not isinstance(with_clause, dict):
                findings.append(finding('review', 'WITH_UNRESOLVED', loc, 'Cannot inspect with: mapping'))
                continue
            kind, days = retention_value(with_clause.get('retention-days'))
            if kind == 'dynamic':
                findings.append(finding('review', 'DYNAMIC_RETENTION', loc, 'Retention-days expression cannot be evaluated offline'))
            elif kind == 'invalid':
                findings.append(finding('high', 'INVALID_RETENTION', loc, 'Retention-days must be 0 or a positive number of days'))
            elif kind == 'number' and days is not None:
                if days < 0 or days > max_cap:
                    findings.append(finding('high', 'OUT_OF_RANGE_RETENTION', loc, f'Retention {days} days outside modeled {visibility} limit (0 for default, max {max_cap})'))
                elif policy_days is not None and days > policy_days:
                    findings.append(finding('review', 'EXCEEDS_SUPPLIED_POLICY', loc, f'Retention {days} days exceeds supplied effective policy {policy_days} days'))
                elif minimum_days is not None and days != 0 and days < minimum_days:
                    findings.append(finding('review', 'BELOW_REQUIRED_WINDOW', loc, f'Retention {days} days below stated minimum {minimum_days} days'))
            if kind == 'default' or (kind == 'number' and days == 0):
                if minimum_days is not None:
                    if policy_days is None:
                        findings.append(finding('review', 'DEFAULT_RETENTION_UNKNOWN', loc, 'Default retention depends on live repository/org/enterprise policy'))
                    elif policy_days < minimum_days:
                        findings.append(finding('review', 'DEFAULT_BELOW_REQUIRED_WINDOW', loc, f'Supplied policy {policy_days} days below stated minimum {minimum_days} days'))
    return sorted(findings, key=lambda f: (f['location'], f['code']))


def collect(paths, visibility='unknown', policy_days=None, minimum_days=None):
    collected = []
    for path in paths:
        if path.is_dir():
            files = sorted(set(path.glob('*.yml')) | set(path.glob('*.yaml')))
        elif path.is_file():
            files = [path]
        else:
            raise ValueError(f'No such workflow path: {path}')
        if not files:
            raise ValueError(f'No YAML workflows at: {path}')
        for file in files:
            try:
                doc = yaml.safe_load(file.read_text(encoding='utf-8'))
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                raise ValueError(f'{file}: {exc}') from exc
            collected.extend(analyze_doc(doc, file.name, visibility=visibility, policy_days=policy_days, minimum_days=minimum_days))
    return sorted(collected, key=lambda f: (f['location'], f['code']))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('workflow', nargs='+', type=Path, help='Workflow YAML files or directory containing them')
    p.add_argument('--visibility', choices=('unknown','public','private'), default='unknown')
    p.add_argument('--policy-days', type=int, help='Effective repo/org/enterprise retention ceiling supplied by operator')
    p.add_argument('--minimum-days', type=int, help='Required artifact availability window supplied by operator')
    p.add_argument('--format', choices=('text','json'), default='text')
    p.add_argument('--strict', action='store_true', help='Exit 2 when findings are present')
    args = p.parse_args(argv)
    cap = {'unknown':400,'public':90,'private':400}[args.visibility]
    if args.policy_days is not None and not 1 <= args.policy_days <= cap:
        p.error(f'--policy-days must be 1 to {cap} for selected visibility')
    if args.minimum_days is not None and not 1 <= args.minimum_days <= 400:
        p.error('--minimum-days must be 1 to 400')
    try:
        findings = collect(args.workflow, visibility=args.visibility,policy_days=args.policy_days,minimum_days=args.minimum_days)
    except ValueError as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 1
    if args.format == 'json':
        print(json.dumps({'count':len(findings),'findings':findings},indent=2))
    else:
        for f in findings:
            print(f"{f['severity'].upper()} [{f['code']}] {f['location']}: {f['message']}")
        print(f'Findings: {len(findings)} (policy is supplied, not fetched from GitHub)')
    return 2 if args.strict and findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
