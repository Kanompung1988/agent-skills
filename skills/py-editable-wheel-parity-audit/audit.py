#!/usr/bin/env python3
"""Read-only parity checks for regular and PEP 660 editable wheel metadata."""
import argparse,json,re,sys
from collections import Counter
from pathlib import Path
from email.parser import BytesParser
from email.policy import default
from zipfile import ZipFile,BadZipFile
def read(path):
    try:
        with ZipFile(path) as archive:
            names=archive.namelist()
            if len(names)>100000 or any(n.startswith('/') or '..' in n.split('/') or '\\' in n for n in names): raise ValueError('unsafe wheel members')
            metadata=[n for n in names if n.endswith('.dist-info/METADATA') and len(n.split('/'))==2]
            if len(metadata)!=1: raise ValueError('expected exactly one .dist-info/METADATA')
            root=metadata[0].rsplit('/',1)[0]+'/'
            if root+'WHEEL' not in names: raise ValueError('missing WHEEL')
            result={}
            for name in (metadata[0],root+'WHEEL',root+'entry_points.txt'):
                if name in names:
                    info=archive.getinfo(name)
                    if info.file_size>2000000: raise ValueError('metadata exceeds 2 MB')
                    with archive.open(name) as stream: value=stream.read(2000001)
                    if len(value)>2000000: raise ValueError('metadata exceeds 2 MB')
                    result[name.split('/')[-1]]=value
            return result
    except (OSError,BadZipFile,EOFError,RuntimeError) as e:
        raise ValueError(f'unreadable wheel: {e}') from e
def inspect(normal,editable,allowed=()):
    files_a=read(normal);files_b=read(editable)
    a=BytesParser(policy=default).parsebytes(files_a['METADATA'])
    b=BytesParser(policy=default).parsebytes(files_b['METADATA'])
    issues=[]
    def add(code,severity,detail): issues.append({'code':code,'severity':severity,'detail':detail})
    for role,meta in (('normal',a),('editable',b)):
        if not meta.get('Name') or not meta.get('Version'):add('MISSING_ID','error',role+' is missing Name/Version')
    norm=lambda v:re.sub(r'[-_.]+','-',str(v)).lower()
    if a.get('Name') and b.get('Name') and norm(a['Name'])!=norm(b['Name']):add('NAME_DRIFT','error','Name differs')
    if a.get('Version') and b.get('Version') and str(a['Version'])!=str(b['Version']):add('VERSION_DRIFT','error','Version differs')
    def headers(meta):return Counter((k.lower(),str(v).strip()) for k,v in meta.raw_items() if k.lower() not in {'name','version','requires-dist'})
    if headers(a)!=headers(b) or a.get_payload()!=b.get_payload():add('CORE_METADATA_DRIFT','error','core metadata differs')
    reqa=Counter(str(v).strip() for v in a.get_all('Requires-Dist',[]))
    reqb=Counter(str(v).strip() for v in b.get_all('Requires-Dist',[]))
    for dep in sorted((reqa-reqb).elements()):add('DROPPED_DEPENDENCY','error',dep)
    for dep in sorted((reqb-reqa).elements()):
        if dep not in allowed:add('EDITABLE_ONLY_DEPENDENCY','review',dep)
    if files_a.get('entry_points.txt')!=files_b.get('entry_points.txt'):add('ENTRY_POINTS_DRIFT','error','entry_points.txt differs')
    return sorted(issues,key=lambda v:(v['severity'],v['code'],v['detail']))
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('regular',type=Path);parser.add_argument('editable',type=Path)
    parser.add_argument('--allow-extra',action='append',default=[])
    parser.add_argument('--strict',action='store_true')
    parser.add_argument('--format',choices=('json','text'),default='text')
    opts=parser.parse_args(argv)
    try:findings=inspect(opts.regular,opts.editable,opts.allow_extra)
    except ValueError as e:print('input error:',e,file=sys.stderr);return 1
    if opts.format=='json':print(json.dumps({'findings':findings},indent=2))
    else:
        print('Findings:',len(findings))
        for f in findings:print(f["severity"],f["code"],f["detail"])
    return 2 if any(f['severity']=='error' or opts.strict for f in findings) else 0
if __name__=='__main__':sys.exit(main())
