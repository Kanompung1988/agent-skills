#!/usr/bin/env python3
"""Offline Kubernetes Ingress TLS host and Secret metadata review."""
import argparse
import json
import sys
from pathlib import Path
import yaml

MAX_BYTES = 1_000_000

def mapping(v):return v if isinstance(v,dict) else {}
def sequence(v):return v if isinstance(v,list) else []
def key(doc):
    meta=mapping(doc.get('metadata'))
    return (str(meta.get('namespace') or 'default'),str(meta.get('name') or '<unnamed>'))

def inspect(paths):
    files=[]
    for p in paths:
        if p.is_dir(): files.extend(sorted(x for x in p.rglob('*') if x.suffix in ('.yaml','.yml') and x.is_file()))
        else: files.append(p)
    docs=[]
    results=[]
    def emit(code,severity,origin,message):results.append(dict(code=code,severity=severity,resource=origin,message=message))
    for file in sorted(set(files)):
        if not file.is_file():raise ValueError(f'file not found: {file}')
        if file.stat().st_size>MAX_BYTES:raise ValueError(f'YAML file exceeds 1 MB limit: {file}')
        try:
            for document in yaml.safe_load_all(file.read_text(encoding='utf-8')):
                if document is None:continue
                if not isinstance(document,dict):
                    emit('INVALID_DOCUMENT','error',file.name,'non-mapping YAML document')
                else:docs.append(document)
        except (yaml.YAMLError,UnicodeError) as exc:raise ValueError(f'invalid YAML: {file}: {exc}') from exc
    secrets={key(d):d for d in docs if d.get('kind')=='Secret'}
    for doc in docs:
        if doc.get('kind')!='Ingress' or doc.get('apiVersion')!='networking.k8s.io/v1':continue
        namespace,name=key(doc)
        origin=f'{namespace}/{name}'
        spec=mapping(doc.get('spec'))
        tls=sequence(spec.get('tls'))
        rules={str(mapping(rule).get('host','')).lower().rstrip('.') for rule in sequence(spec.get('rules')) if mapping(rule).get('host')}
        tls_hosts=set()
        for item in tls:
            if not isinstance(item,dict):
                emit('INVALID_TLS','error',origin,'TLS entry is not a mapping');continue
            hosts=sequence(item.get('hosts'))
            for host in hosts:
                h=str(host).lower().rstrip('.')
                if h in tls_hosts: emit('DUPLICATE_TLS_HOST','review',origin,f'TLS host {h!r} appears more than once')
                tls_hosts.add(h)
                if h not in rules:emit('TLS_HOST_WITHOUT_RULE','review',origin,f'TLS host {h!r} does not exactly match an Ingress rule host')
            secret=item.get('secretName')
            if not secret:
                emit('NO_SECRET_NAME','review',origin,'TLS entry has no secretName; controller-dependent behavior')
                continue
            sec=secrets.get((namespace,str(secret)))
            if sec is None:
                emit('UNRESOLVED_SECRET','review',origin,f'{namespace}/{secret}: Secret is absent from supplied batch, not necessarily cluster')
                continue
            if sec.get('type')!='kubernetes.io/tls':
                emit('SECRET_TYPE','error',origin,f'{namespace}/{secret}: expected kubernetes.io/tls type')
            keys=set(mapping(sec.get('data')))|set(mapping(sec.get('stringData')))
            for expected in ('tls.crt','tls.key'):
                if expected not in keys:emit('SECRET_KEY','error',origin,f'{namespace}/{secret}: missing {expected} key')
        for rule in sorted(rules-tls_hosts):
            if tls:emit('RULE_NOT_IN_TLS','review',origin,f'rule host {rule!r} is not covered by declared TLS hosts')
    return sorted(results,key=lambda f:(f['resource'],f['code'],f['message']))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('paths',type=Path,nargs='+',help='local YAML files or directories (synthetic/sanitized manifests only)')
    p.add_argument('--json',action='store_true',dest='as_json')
    p.add_argument('--fail-on',choices=('error','review','never'),default='error')
    a=p.parse_args(argv)
    try: found=inspect(a.paths)
    except (OSError,ValueError) as exc:
        print(f'input error: {exc}',file=sys.stderr);return 1
    if a.as_json:print(json.dumps({'findings':found,'counts':{'error':sum(x['severity']=='error' for x in found),'review':sum(x['severity']=='review' for x in found)}},indent=2))
    else:
        for x in found:print(f"{x['resource']} {x['severity'].upper()} {x['code']}: {x['message']}")
        print(f'{len(found)} finding(s)')
    return 2 if a.fail_on!='never' and any(x['severity']=='error' or a.fail_on=='review' for x in found) else 0

if __name__=='__main__':sys.exit(main())
