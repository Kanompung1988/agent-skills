#!/usr/bin/env python3
"""Read-only GitHub Actions deployment-environment contract reviewer (no API calls)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any
import yaml

class Yaml12Loader(yaml.SafeLoader):
    pass
Yaml12Loader.yaml_implicit_resolvers = {
    key: [(tag, pat) for tag, pat in rules if tag != 'tag:yaml.org,2002:bool']
    for key, rules in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
Yaml12Loader.add_implicit_resolver('tag:yaml.org,2002:bool',re.compile(r'^(?:true|false|True|False|TRUE|FALSE)$'),list('tTfF'))

DEPLOY_RE = re.compile(r'(?:deploy|release|publish|promote|production|prod|rollout)',re.I)
SENSITIVE_NAMES = {'production','prod','live','staging'}

def finding(rule: str, file: str, job: str, detail: str, severity: str='review') -> dict:
    return {'rule':rule,'file':file,'job':job,'severity':severity,'detail':detail}

def load_inventory(path: Path | None) -> dict | None:
    if path is None: return None
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('environments'), dict):
        raise ValueError('inventory needs an environments mapping')
    entries={}
    for name, cfg in data['environments'].items():
        if not isinstance(name,str) or not isinstance(cfg,dict):
            raise ValueError('each environment entry must be an object')
        entries[name.casefold()]=cfg
    return entries

def environment_name(spec: Any) -> str | None:
    if isinstance(spec,str): return spec.strip()
    if isinstance(spec,dict) and isinstance(spec.get('name'),str): return spec['name'].strip()
    return None

def audit_document(doc: Any, file: str, inventory: dict | None) -> list[dict]:
    out=[]
    if not isinstance(doc,dict): raise ValueError('workflow must be YAML mapping')
    jobs=doc.get('jobs',{})
    if not isinstance(jobs,dict): raise ValueError('jobs must be YAML mapping')
    for job_id, job in jobs.items():
        jid=str(job_id)
        if not isinstance(job,dict): continue
        name=environment_name(job.get('environment'))
        maybe_deploy=bool(DEPLOY_RE.search(jid+' '+str(job.get('name',''))))
        if maybe_deploy and not name:
            out.append(finding('ENV001',file,jid,'Deployment-like job has no environment binding; review whether protected environments are required.'))
        if job.get('environment') is not None and not name:
            out.append(finding('ENV002',file,jid,'Environment is malformed or expression-only; cannot resolve the gate statically.'))
        if not name: continue
        if '${{' in name:
            out.append(finding('ENV003',file,jid,'Dynamic environment name: verify every resolved value is protected.'))
            continue
        if inventory is None:
            out.append(finding('ENV004',file,jid,f'Environment {name!r} cannot be verified without a reviewed settings inventory.','info'))
            continue
        cfg=inventory.get(name.casefold())
        if cfg is None:
            out.append(finding('ENV005',file,jid,f'Environment {name!r} absent from the supplied inventory; GitHub may create it without protection rules.'))
            continue
        if name.casefold() not in SENSITIVE_NAMES and not maybe_deploy: continue
        reviewers=cfg.get('required_reviewers')
        if reviewers is None or type(reviewers) is not int or reviewers < 1:
            out.append(finding('ENV006',file,jid,f'No required reviewers recorded for environment {name!r}.'))
        if cfg.get('prevent_self_review') is not True:
            out.append(finding('ENV007',file,jid,f'Self-review prevention not confirmed for {name!r}.','info'))
        if cfg.get('can_admins_bypass') is not False:
            out.append(finding('ENV008',file,jid,f'Admin bypass restriction not confirmed for {name!r}.','info'))
        branch_policy=cfg.get('deployment_branch_policy')
        if not isinstance(branch_policy,dict) or not (branch_policy.get('protected_branches') is True or branch_policy.get('custom_branch_policies') is True):
            out.append(finding('ENV009',file,jid,f'No deployment branch/tag restriction recorded for {name!r}.'))
    return out

def audit(path: Path, inventory: dict | None=None) -> tuple[int,list[dict]]:
    if path.is_file(): files=[path]
    elif path.is_dir(): files=sorted(p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in ('.yml','.yaml') and '.git' not in p.parts)
    else: raise ValueError('input path does not exist')
    if not files: raise ValueError('no workflow YAML files found')
    result=[]
    for file in files:
        if file.stat().st_size > 1_000_000: raise ValueError(f'file too large: {file}')
        doc=yaml.load(file.read_text(encoding='utf-8'),Loader=Yaml12Loader)
        result.extend(audit_document(doc,str(file),inventory))
    return len(files),sorted(result,key=lambda x:(x['file'],x['job'],x['rule']))

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path)
    parser.add_argument('--inventory',type=Path,help='optional reviewed GitHub environment settings inventory (not live API verification)')
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args(argv)
    try:
        count,items=audit(args.path,load_inventory(args.inventory))
        payload={'files_scanned':count,'inventory_supplied':args.inventory is not None,'findings':items}
        if args.json: print(json.dumps(payload,indent=2,sort_keys=True))
        else:
            for item in items: print(f"{item['file']}:{item['job']} [{item['rule']}] {item['detail']}")
            print(f'{count} files; {len(items)} findings')
        return 1 if items else 0
    except (OSError,ValueError,yaml.YAMLError,json.JSONDecodeError) as error:
        print(f'Input error: {error}',file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
