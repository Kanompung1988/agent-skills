#!/usr/bin/env python3
"""Offline review of Terraform moved/removed state transition declarations."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

BLOCK = re.compile(r'\b(moved|removed)\s*\{')
ADDR = re.compile(r'^(?:module\.[A-Za-z_][\w-]*\.)*(?:[A-Za-z_][\w-]*\.){1,2}[A-Za-z_][\w-]*(?:\[[0-9]+\])?$|^module\.[A-Za-z_][\w-]*(?:\.module\.[A-Za-z_][\w-]*)*$')


def mask_noncode(src: str) -> str:
    """Preserve offsets/newlines; hide HCL comments, string bodies and heredocs."""
    out=list(src); n=len(src); i=0
    def hide(a,b):
        for k in range(a,b):
            if src[k] not in '\r\n': out[k]=' '
    while i<n:
        if src.startswith('/*',i):
            j=src.find('*/',i+2);j=n if j<0 else j+2;hide(i,j);i=j;continue
        if src.startswith('//',i) or src[i]=='#':
            j=src.find('\n',i);j=n if j<0 else j;hide(i,j);i=j;continue
        if src[i]=='"':
            j=i+1
            while j<n:
                if src[j]=='\\': j+=2;continue
                if src[j]=='"':j+=1;break
                j+=1
            hide(i,min(j,n));i=j;continue
        if src.startswith('<<',i):
            m=re.match(r'<<-?([A-Za-z_][A-Za-z0-9_]*)',src[i:])
            if m:
                tag=m.group(1);start=i;cur=src.find('\n',i)
                if cur<0:cur=n
                else:
                    cur+=1
                    while cur<n:
                        end=src.find('\n',cur);end=n if end<0 else end
                        if src[cur:end].strip()==tag:
                            cur=end;break
                        cur=end+1
                hide(start,cur);i=cur;continue
        i+=1
    return ''.join(out)


def finding(rule,file,line,detail,severity='review'):
    return {'rule':rule,'file':str(file),'line':line,'severity':severity,'detail':detail}


def blocks(source: str):
    masked=mask_noncode(source)
    for match in BLOCK.finditer(masked):
        depth=1;start=match.end();j=start
        while j<len(masked) and depth:
            if masked[j]=='{':depth+=1
            if masked[j]=='}':depth-=1
            j+=1
        if depth:raise ValueError(f'unclosed {match.group(1)} block at line {source.count(chr(10),0,match.start())+1}')
        yield match.group(1),masked[start:j-1],source.count('\n',0,match.start())+1


def assignment(body,key):
    found=re.search(r'(?m)^\s*'+re.escape(key)+r'\s*=\s*([^\n\r]*)',body)
    return found.group(1).strip() if found else None


def analyze(file:Path):
    source=file.read_text(encoding='utf-8')
    issues=[]; moves=[]; removals=[]
    for kind,body,line in blocks(source):
        src=assignment(body,'from')
        if kind=='moved':
            dst=assignment(body,'to')
            if src is None or dst is None:
                issues.append(finding('TFM001',file,line,'moved block needs both from and to.'));continue
            if not ADDR.fullmatch(src) or not ADDR.fullmatch(dst):
                issues.append(finding('TFM002',file,line,'Address is not in the supported static subset; inspect manually.','info'));continue
            if src==dst:issues.append(finding('TFM003',file,line,'moved source and target are identical.'))
            moves.append((src,dst,line))
        else:
            if not src:
                issues.append(finding('TFR001',file,line,'removed block needs a from address.'));continue
            if not ADDR.fullmatch(src):
                issues.append(finding('TFR002',file,line,'Removed address is outside the supported static subset; inspect manually.','info'));continue
            nested=re.search(r'\blifecycle\s*\{([^{}]*)\}',body,re.S)
            destroy=assignment(nested.group(1),'destroy') if nested else None
            if destroy != 'false':
                issues.append(finding('TFR003',file,line,'State handoff is not explicitly destroy = false; Terraform may destroy the real object.'))
            removals.append((src,line))
    return issues,moves,removals


def audit(path:Path):
    if path.is_file():files=[path]
    elif path.is_dir():files=sorted(p for p in path.rglob('*.tf') if p.is_file() and not any(part in {'.terraform','.git'} for part in p.parts))
    else:raise ValueError('path not found')
    if not files:raise ValueError('no .tf files found')
    issues=[];moves=[];removals=[]
    for file in files:
        if file.stat().st_size>1_000_000:raise ValueError('file exceeds 1MB')
        found,mm,rr=analyze(file)
        issues.extend(found);moves.extend((a,b,str(file),line) for a,b,line in mm);removals.extend((a,str(file),line) for a,line in rr)
    sources={};targets={};removed={}
    for src,dst,file,line in moves:
        if src in sources: issues.append(finding('TFM004',file,line,f'Duplicate move source {src}.'))
        sources[src]=dst
        if dst in targets: issues.append(finding('TFM005',file,line,f'Multiple moves into target {dst}.'))
        targets[dst]=src
    for src,file,line in removals:
        if src in removed:issues.append(finding('TFR004',file,line,f'Duplicate removed source {src}.'))
        removed[src]=line
        if src in sources or src in targets:issues.append(finding('TFR005',file,line,f'Removed address {src} overlaps a move declaration.'))
    for src,dst,file,line in moves:
        visited={src};cur=dst
        while cur in sources:
            if cur in visited:
                issues.append(finding('TFM006',file,line,f'Move cycle detected from {src}.'));break
            visited.add(cur);cur=sources[cur]
    issues.sort(key=lambda x:(x['file'],x['line'],x['rule']))
    return len(files),issues


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path)
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args(argv)
    try:
        count,findings=audit(args.path)
        if args.json:print(json.dumps({'files_scanned':count,'findings':findings},indent=2,sort_keys=True))
        else:
            for f in findings:print(f"{f['file']}:{f['line']} [{f['rule']}] {f['detail']}")
            print(f'{count} files; {len(findings)} findings')
        return 1 if findings else 0
    except (OSError,ValueError,UnicodeError) as e:
        print(f'Input error: {e}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
