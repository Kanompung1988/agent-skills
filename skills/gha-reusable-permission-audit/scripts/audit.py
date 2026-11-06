#!/usr/bin/env python3
"""Offline GitHub Actions reusable workflow caller policy review."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml
COMMIT=re.compile(r'^[a-fA-F0-9]{40}$')
EXTERNAL=re.compile(r'^[^@\s/]+/[^@\s/]+/\.github/workflows/[^@\s]+@([^@\s]+)$')
WRITE={'actions','attestations','contents','deployments','id-token','issues','packages','pull-requests','security-events','workflows'}

def audit(data):
    if not isinstance(data,dict) or not isinstance(data.get('jobs'),dict):
        raise ValueError('expected jobs mapping')
    findings=[]
    def add(rule,severity,job,msg):
        findings.append({'rule':rule,'severity':severity,'job':job,'message':msg})
    events=data.get('on')
    if isinstance(events,dict):
        triggers=list(events)
    elif isinstance(events,list):
        triggers=events
    else:
        triggers=[events] if events else []
    top=data.get('permissions')
    for job,conf in sorted(data['jobs'].items()):
        if not isinstance(conf,dict):
            raise ValueError('invalid job configuration')
        uses=conf.get('uses')
        if uses is None:
            continue
        if not isinstance(uses,str):
            add('GRP006','review',job,'non-string reusable workflow reference')
            continue
        ext=EXTERNAL.fullmatch(uses)
        if uses.startswith('./.github/workflows/'):
            if '@' in uses or '..' in uses:
                add('GRP006','review',job,'invalid local reusable workflow path')
        elif ext:
            if not COMMIT.fullmatch(ext.group(1)):
                add('GRP001','review',job,'external reusable workflow is not pinned to full SHA')
        else:
            add('GRP006','review',job,'unrecognized reusable workflow reference')
        secret=conf.get('secrets')
        if secret=='inherit' and ext:
            add('GRP002','high',job,'external called workflow receives inherited caller secrets')
        elif isinstance(secret,dict) and ext:
            add('GRP007','review',job,'external call passes mapped secrets; verify trust')
        perm=conf.get('permissions',top)
        if perm is None:
            add('GRP003','review',job,'no explicit GITHUB_TOKEN permissions scope')
        elif perm=='write-all':
            add('GRP004','high',job,'write-all token permission scope')
        elif isinstance(perm,dict):
            broad=sorted(str(k) for k,v in perm.items() if k in WRITE and v=='write')
            if broad:
                add('GRP005','review',job,'caller has write token scopes: '+', '.join(broad))
        elif perm not in ('read-all','{}'):
            add('GRP006','review',job,'unknown permissions form')
        if 'pull_request_target' in triggers and (secret=='inherit' or perm=='write-all'):
            add('GRP008','high',job,'pull_request_target plus inherited secrets or broad token')
    return findings

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('file',type=Path)
    p.add_argument('--json',action='store_true')
    a=p.parse_args()
    try:
        if a.file.is_symlink() or not a.file.is_file() or a.file.stat().st_size>1000000:
            raise ValueError('input must be regular non-symlink YAML under 1 MB')
        doc=yaml.load(a.file.read_text(encoding='utf-8'),Loader=yaml.BaseLoader)
        findings=audit(doc)
    except (ValueError,OSError,UnicodeError,yaml.YAMLError) as e:
        print('Input error: '+str(e),file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps({'count':len(findings),'findings':findings},indent=2))
    else:
        for f in findings:
            print(f['rule'],f['severity'],f['job'],f['message'])
        print(len(findings),'finding(s)')
    return 1 if findings else 0

if __name__=='__main__':
    sys.exit(main())
