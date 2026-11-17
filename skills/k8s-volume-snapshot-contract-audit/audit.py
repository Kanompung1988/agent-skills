#!/usr/bin/env python3
"""Read-only, batch-scoped CSI snapshot manifest reviewer."""
import argparse,json,sys
from pathlib import Path
import yaml
API='snapshot.storage.k8s.io/v1'
KINDS={'VolumeSnapshotClass','VolumeSnapshot','VolumeSnapshotContent','PersistentVolumeClaim'}
def mapval(v):return v if isinstance(v,dict) else {}
def label(o):
 m=mapval(o.get('metadata'))
 return f"{o.get('kind')}/{m.get('namespace') or 'default'}/{m.get('name') or '<unnamed>'}"
def load(paths):
 files=[]
 for raw in paths:
  p=Path(raw)
  if p.is_dir():files.extend(sorted(x for x in p.rglob('*') if x.is_file() and not x.is_symlink() and x.suffix.lower() in ('.yaml','.yml')))
  elif p.is_file() and not p.is_symlink():files.append(p)
  else:raise ValueError(f'not a regular YAML file/directory: {raw}')
 results=[]
 for path in files:
  if path.stat().st_size>2000000:raise ValueError(f'YAML exceeds 2 MB: {path}')
  try:
   for o in yaml.safe_load_all(path.read_text(encoding='utf-8')):
    if o is None:continue
    if not isinstance(o,dict):raise ValueError(f'non-mapping YAML in {path}')
    if o.get('kind') in KINDS and (o.get('apiVersion')==API or o.get('kind')=='PersistentVolumeClaim' and o.get('apiVersion')=='v1'):
     results.append((str(path),o))
  except yaml.YAMLError as e:raise ValueError(f'invalid YAML in {path}: {e}') from e
 return results
def audit(docs):
 problems=[]
 def emit(code,severity,file,obj,detail):
  problems.append(dict(code=code,severity=severity,file=file,object=label(obj),detail=detail))
 groups={k:{} for k in KINDS}
 for file,o in docs:
  kind=o['kind'];m=mapval(o.get('metadata'));name=m.get('name')
  if not isinstance(name,str) or not name:emit('MISSING_NAME','error',file,o,'metadata.name is required');continue
  key=name if kind in ('VolumeSnapshotClass','VolumeSnapshotContent') else (m.get('namespace') or 'default',name)
  if key in groups[kind]:emit('DUPLICATE_OBJECT','error',file,o,'duplicate identity in supplied YAML')
  else:groups[kind][key]=(file,o)
 cls=groups['VolumeSnapshotClass'];snap=groups['VolumeSnapshot'];cont=groups['VolumeSnapshotContent'];pvcs=groups['PersistentVolumeClaim']
 defaults={}
 for file,o in cls.values():
  driver=o.get('driver');policy=o.get('deletionPolicy')
  if not isinstance(driver,str) or not driver:emit('CLASS_DRIVER','error',file,o,'driver is required')
  if policy not in ('Delete','Retain'):emit('CLASS_POLICY','error',file,o,'invalid deletionPolicy')
  elif policy=='Delete':emit('CLASS_DELETE','review',file,o,'Delete may remove backing snapshots')
  a=mapval(mapval(o.get('metadata')).get('annotations'))
  if str(a.get('snapshot.storage.kubernetes.io/is-default-class','')).lower()=='true':defaults.setdefault(driver,[]).append((file,o))
 for driver,matches in defaults.items():
  if len(matches)>1:
   for file,o in matches:emit('MULTIPLE_DEFAULTS','error',file,o,f'multiple defaults for CSI driver {driver}')
 for file,o in cont.values():
  spec=mapval(o.get('spec'));source=mapval(spec.get('source'))
  if sum(bool(source.get(k)) for k in ('snapshotHandle','volumeHandle'))!=1:emit('CONTENT_SOURCE','error',file,o,'exactly one volumeHandle or snapshotHandle required')
  policy=spec.get('deletionPolicy')
  if policy not in ('Delete','Retain'):emit('CONTENT_POLICY','error',file,o,'invalid deletionPolicy')
  elif policy=='Delete':emit('CONTENT_DELETE','review',file,o,'underlying CSI snapshot may be deleted')
  ref=mapval(spec.get('volumeSnapshotRef'))
  if not ref.get('name') or not ref.get('namespace'):emit('CONTENT_REF','error',file,o,'volumeSnapshotRef name and namespace are required')
 for (ns,name),(file,o) in snap.items():
  spec=mapval(o.get('spec'));source=mapval(spec.get('source'))
  pvc=source.get('persistentVolumeClaimName');content=source.get('volumeSnapshotContentName')
  if bool(pvc)==bool(content):emit('SNAPSHOT_SOURCE','error',file,o,'exactly one PVC/content source required')
  if pvc and (ns,pvc) not in pvcs:emit('PVC_UNRESOLVED','review',file,o,'PVC absent from supplied YAML; may exist in cluster')
  if spec.get('volumeSnapshotClassName') and spec['volumeSnapshotClassName'] not in cls:
   emit('CLASS_UNRESOLVED','review',file,o,'named class absent from supplied YAML')
  if content:
   if content not in cont:emit('CONTENT_UNRESOLVED','review',file,o,'content absent from supplied YAML')
   else:
    ref=mapval(mapval(cont[content][1].get('spec')).get('volumeSnapshotRef'))
    if (ref.get('namespace'),ref.get('name'))!=(ns,name):emit('CONTENT_BINDING','error',file,o,'content refers to a different snapshot')
 for (ns,name),(file,pvc) in pvcs.items():
  spec=mapval(pvc.get('spec'));ds=mapval(spec.get('dataSource'))
  if ds.get('kind')!='VolumeSnapshot':continue
  if ds.get('apiGroup')!='snapshot.storage.k8s.io':emit('RESTORE_GROUP','error',file,pvc,'wrong apiGroup on VolumeSnapshot dataSource')
  s=snap.get((ns,ds.get('name')))
  if not s:emit('RESTORE_UNRESOLVED','review',file,pvc,'snapshot absent from supplied YAML namespace');continue
  content=mapval(mapval(s[1].get('spec')).get('source')).get('volumeSnapshotContentName')
  if content in cont:
   o=cont[content][1];mode=mapval(o.get('spec')).get('sourceVolumeMode')
   ann=mapval(mapval(o.get('metadata')).get('annotations'))
   allow=str(ann.get('snapshot.storage.kubernetes.io/allow-volume-mode-change','')).lower()=='true'
   if mode in ('Filesystem','Block') and spec.get('volumeMode','Filesystem')!=mode and not allow:
    emit('RESTORE_MODE','error',file,pvc,'restore volumeMode differs without allow-volume-mode-change')
 return sorted(problems,key=lambda v:(v['file'],v['object'],v['code']))
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('paths',nargs='+');p.add_argument('--format',choices=('text','json'),default='text');p.add_argument('--strict',action='store_true')
 args=p.parse_args(argv)
 try:
  docs=load(args.paths)
  if not docs:raise ValueError('no snapshot/PVC documents found')
  findings=audit(docs)
 except (ValueError,OSError,UnicodeError) as e:print('input error:',e,file=sys.stderr);return 1
 if args.format=='json':print(json.dumps({'objects':len(docs),'findings':findings},indent=2))
 else:
  print('Scanned:',len(docs),'Findings:',len(findings))
  for f in findings:print(f['severity'],f['code'],f['object'],f['detail'])
 return 2 if any(f['severity']=='error' or args.strict for f in findings) else 0
if __name__=='__main__':sys.exit(main())
