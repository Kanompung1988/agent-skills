#!/usr/bin/env python3
"""Offline policy-aware Namespace Pod Security Admission label review."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml

PREFIX = 'pod-security.kubernetes.io/'
MODES = ('enforce', 'audit', 'warn')
LEVELS = ('privileged', 'baseline', 'restricted')
VERSION = re.compile(r'^v[0-9]+\.[0-9]+$')

class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    out = {}
    for kn, vn in node.value:
        k=loader.construct_object(kn,deep=True)
        if not isinstance(k,(str,int,float,bool)):
            raise ValueError('unsupported YAML key type')
        if k in out:
            raise ValueError(f'duplicate YAML key: {k}')
        out[k]=loader.construct_object(vn,deep=True)
    return out

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)


def load(path):
    if path.stat().st_size>2_000_000:
        raise ValueError('file exceeds 2 MB safety limit')
    docs=list(yaml.load_all(path.read_text(encoding='utf-8'),Loader=UniqueLoader))
    if not docs: raise ValueError('empty YAML')
    if any(doc is not None and not isinstance(doc,dict) for doc in docs):
        raise ValueError('all YAML documents must be mappings')
    return [d for d in docs if isinstance(d,dict)]


def audit(documents,minimum='baseline',pin_versions=False,exempt=()):
    if minimum not in ('none',)+LEVELS:
        raise ValueError('invalid minimum')
    findings=[]
    seen={}
    exemptions=set(exempt)
    def issue(rule,severity,name,detail):
        findings.append({'rule':rule,'severity':severity,'namespace':name,'message':detail})
    for doc in documents:
        if doc.get('kind')!='Namespace':continue
        meta=doc.get('metadata')
        if not isinstance(meta,dict):raise ValueError('Namespace metadata must be a mapping')
        name=meta.get('name')
        if not isinstance(name,str) or not name:
            raise ValueError('Namespace must have metadata.name')
        labels=meta.get('labels') or {}
        annotations=meta.get('annotations') or {}
        if not isinstance(labels,dict) or not isinstance(annotations,dict):
            raise ValueError('labels and annotations must be mappings')
        relevant={k:v for k,v in labels.items() if isinstance(k,str) and k.startswith(PREFIX)}
        if name in seen:
            issue('DUPLICATE_NAMESPACE','error',name,'Repeated Namespace manifest; effective labels depend on apply ordering')
        seen[name]=relevant
        if name in exemptions:continue
        for k in annotations:
            if isinstance(k,str) and k.startswith(PREFIX):
                issue('PSA_ANNOTATION','review',name,f'{k} is an annotation, not an effective Namespace label')
        for k,v in relevant.items():
            suffix=k[len(PREFIX):]
            if suffix not in MODES and suffix not in tuple(m+'-version' for m in MODES):
                issue('UNKNOWN_PSA_LABEL','review',name,f'Unknown Pod Security Admission label {k}')
                continue
            if suffix in MODES:
                if not isinstance(v,str) or v not in LEVELS:
                    issue('INVALID_LEVEL','error',name,f'{suffix} must be privileged, baseline, or restricted')
            else:
                if not isinstance(v,str) or (v!='latest' and not VERSION.fullmatch(v)):
                    issue('INVALID_VERSION','error',name,f'{suffix} must be latest or vMAJOR.MINOR')
                if suffix[:-8] not in relevant and PREFIX+suffix[:-8] not in relevant:
                    # A version without mode is allowed by API but can be misleading to operators.
                    issue('ORPHAN_VERSION','review',name,f'{suffix} is set without corresponding mode level')
        enforce=relevant.get(PREFIX+'enforce')
        if minimum!='none':
            if enforce is None:
                issue('MISSING_ENFORCE','review',name,f'No enforce label; desired minimum is {minimum}; cluster-wide defaults are unknown')
            elif enforce in LEVELS and LEVELS.index(enforce)<LEVELS.index(minimum):
                issue('WEAK_ENFORCE','review',name,f'enforce={enforce} below operator minimum {minimum}')
        if enforce=='privileged':
            issue('PRIVILEGED_ENFORCE','review',name,'enforce=privileged allows all Pod Security Standard levels')
        for mode in ('warn','audit'):
            v=relevant.get(PREFIX+mode)
            if v in LEVELS and enforce in LEVELS and LEVELS.index(v)<LEVELS.index(enforce):
                issue('WEAKER_OBSERVABILITY','info',name,f'{mode}={v} is weaker than enforce={enforce}; verify desired telemetry')
        if pin_versions:
            for mode in MODES:
                if relevant.get(PREFIX+mode) in LEVELS and not relevant.get(PREFIX+mode+'-version'):
                    issue('UNPINNED_VERSION','review',name,f'{mode} policy version not pinned; latest behavior can change on upgrade')
    findings.sort(key=lambda x:(x['namespace'],x['rule'],x['message']))
    return findings


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest',type=Path)
    ap.add_argument('--minimum-enforce',choices=['none','baseline','restricted'],default='baseline')
    ap.add_argument('--require-pinned-version',action='store_true')
    ap.add_argument('--exempt',action='append',default=[],help='operator-selected namespace exempt from review')
    ap.add_argument('--format',choices=['json','text'],default='text')
    args=ap.parse_args(argv)
    try: findings=audit(load(args.manifest),args.minimum_enforce,args.require_pinned_version,args.exempt)
    except (OSError,UnicodeError,ValueError,yaml.YAMLError) as exc:
        print(f'Input error: {exc}',file=sys.stderr)
        return 1
    report={'file':str(args.manifest),'finding_count':len(findings),'findings':findings,'status':'review' if findings else 'safe'}
    if args.format=='json':print(json.dumps(report,indent=2))
    else:
        print(f"{report['status'].upper()}: {len(findings)} finding(s) in {args.manifest}")
        for f in findings:print(f"[{f['severity']}] {f['rule']} {f['namespace']}: {f['message']}")
    return 2 if findings else 0

if __name__=='__main__':sys.exit(main())
