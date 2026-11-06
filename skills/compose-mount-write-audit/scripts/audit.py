#!/usr/bin/env python3
"""Offline single-Compose-file bind-mount exposure audit."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml

def hostpath(s):
    return s.startswith(('./','../','/','~/','$')) or bool(re.match(r'^[A-Za-z]:[\\/]',s))

def sensitive(s):
    return s=='/' or any(s==p or s.startswith(p+'/') for p in (
        '/etc','/root','/var/run','/run','/proc','/sys','/dev','/var/lib/docker'))

def audit(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get('services'),dict):
        raise ValueError('services must be mapping')
    found=[]
    def add(rule,severity,service,target,message):
        found.append({'rule':rule,'severity':severity,'service':service,'target':target,'message':message})
    for service,conf in sorted(doc['services'].items()):
        if not isinstance(conf,dict):
            raise ValueError('invalid service')
        if conf.get('volumes_from'):
            add('CMW006','review',service,'-','volumes_from entries not expanded')
        vols=conf.get('volumes',[])
        if vols is None:
            vols=[]
        if not isinstance(vols,list):
            raise ValueError('volumes must be list')
        for i,vol in enumerate(vols):
            target='volume['+str(i)+']'
            if isinstance(vol,str):
                if re.match(r'^[A-Za-z]:[\\/]',vol):
                    add('CMW005','review',service,target,'ambiguous Windows mount')
                    continue
                parts=vol.split(':')
                if len(parts)==1:
                    continue
                if len(parts) not in (2,3) or not all(parts[:2]):
                    add('CMW005','review',service,target,'unrecognized short mount syntax')
                    continue
                src,target=parts[:2]
                if not hostpath(src):
                    continue
                opts=set(parts[2].split(',')) if len(parts)==3 else set()
                if 'rw' in opts and 'ro' in opts:
                    add('CMW005','review',service,target,'conflicting rw and ro')
                    continue
                ro='ro' in opts
            elif isinstance(vol,dict):
                typ=vol.get('type','volume')
                if typ not in ('bind','volume','tmpfs','npipe','image'):
                    add('CMW005','review',service,target,'unrecognized mount type')
                    continue
                if typ!='bind':
                    continue
                src,target=vol.get('source'),vol.get('target',target)
                ro=vol.get('read_only',False)
                if not isinstance(ro,bool) or not isinstance(src,str) or not isinstance(target,str):
                    add('CMW005','review',service,str(target),'invalid long mount fields')
                    continue
            else:
                add('CMW005','review',service,target,'invalid volume entry')
                continue
            if '$' in src:
                add('CMW005','review',service,target,'host path interpolation unresolved')
            elif src.rstrip('/').endswith('/docker.sock'):
                add('CMW001','high',service,target,'Docker API socket can be used even on ro mount')
            elif not ro and (sensitive(src.rstrip('/') or '/') or sensitive(target)):
                add('CMW002','high',service,target,'writable sensitive source or container target')
            elif not ro:
                add('CMW003','review',service,target,'writable bind mount (ro not specified)')
    return found

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('file',type=Path)
    p.add_argument('--json',action='store_true')
    a=p.parse_args()
    try:
        if a.file.is_symlink() or not a.file.is_file() or a.file.stat().st_size>1000000:
            raise ValueError('file must exist, not be symlink, <= 1 MB')
        findings=audit(yaml.safe_load(a.file.read_text(encoding='utf8')))
    except (ValueError,OSError,UnicodeError,yaml.YAMLError) as e:
        print('Input error: '+str(e),file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps({'count':len(findings),'findings':findings},indent=2))
    else:
        for f in findings:
            print(f['rule'],f['severity'],f['service'],f['target'],f['message'])
        print(len(findings),'finding(s)')
    return 1 if findings else 0

if __name__=='__main__':
    sys.exit(main())
