import importlib.util,tempfile,unittest
from pathlib import Path
from contextlib import redirect_stdout,redirect_stderr
from io import StringIO
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def obj(kind,name,spec=None,ns='default',**extra):
 return {'apiVersion':'v1' if kind=='PersistentVolumeClaim' else 'snapshot.storage.k8s.io/v1','kind':kind,'metadata':{'name':name,'namespace':ns},'spec':spec or {},**extra}
def codes(*objs):return [f['code'] for f in audit.audit([('demo.yaml',o) for o in objs])]
class Tests(unittest.TestCase):
 def test_valid_dynamic(self):
  c=obj('VolumeSnapshotClass','cls',driver='driver',deletionPolicy='Retain')
  p=obj('PersistentVolumeClaim','pvc')
  s=obj('VolumeSnapshot','snap',{'volumeSnapshotClassName':'cls','source':{'persistentVolumeClaimName':'pvc'}})
  self.assertEqual(codes(c,p,s),[])
 def test_driver(self):self.assertIn('CLASS_DRIVER',codes(obj('VolumeSnapshotClass','c',deletionPolicy='Retain')))
 def test_class_policy(self):self.assertIn('CLASS_POLICY',codes(obj('VolumeSnapshotClass','c',driver='d',deletionPolicy='Bogus')))
 def test_class_delete(self):self.assertIn('CLASS_DELETE',codes(obj('VolumeSnapshotClass','c',driver='d',deletionPolicy='Delete')))
 def test_ambiguous_default(self):
  a=obj('VolumeSnapshotClass','a',driver='d',deletionPolicy='Retain');b=obj('VolumeSnapshotClass','b',driver='d',deletionPolicy='Retain')
  for o in (a,b):o['metadata']['annotations']={'snapshot.storage.kubernetes.io/is-default-class':'true'}
  self.assertIn('MULTIPLE_DEFAULTS',codes(a,b))
 def test_one_default_each_driver(self):
  a=obj('VolumeSnapshotClass','a',driver='d1',deletionPolicy='Retain');b=obj('VolumeSnapshotClass','b',driver='d2',deletionPolicy='Retain')
  for o in (a,b):o['metadata']['annotations']={'snapshot.storage.kubernetes.io/is-default-class':'true'}
  self.assertNotIn('MULTIPLE_DEFAULTS',codes(a,b))
 def test_missing_source(self):self.assertIn('SNAPSHOT_SOURCE',codes(obj('VolumeSnapshot','s')))
 def test_two_sources(self):self.assertIn('SNAPSHOT_SOURCE',codes(obj('VolumeSnapshot','s',{'source':{'persistentVolumeClaimName':'p','volumeSnapshotContentName':'c'}})))
 def test_missing_pvc_is_review(self):self.assertIn('PVC_UNRESOLVED',codes(obj('VolumeSnapshot','s',{'source':{'persistentVolumeClaimName':'p'}})))
 def test_namespace(self):
  p=obj('PersistentVolumeClaim','p',ns='one');s=obj('VolumeSnapshot','s',{'source':{'persistentVolumeClaimName':'p'}},ns='two')
  self.assertIn('PVC_UNRESOLVED',codes(p,s))
 def test_missing_class(self):self.assertIn('CLASS_UNRESOLVED',codes(obj('VolumeSnapshot','s',{'source':{'persistentVolumeClaimName':'p'},'volumeSnapshotClassName':'absent'})))
 def test_content_source(self):self.assertIn('CONTENT_SOURCE',codes(obj('VolumeSnapshotContent','c',{'deletionPolicy':'Retain','volumeSnapshotRef':{'name':'s','namespace':'default'}})))
 def test_content_policy(self):self.assertIn('CONTENT_POLICY',codes(obj('VolumeSnapshotContent','c',{'source':{'snapshotHandle':'h'},'volumeSnapshotRef':{'name':'s','namespace':'default'}})))
 def test_content_delete(self):self.assertIn('CONTENT_DELETE',codes(obj('VolumeSnapshotContent','c',{'source':{'snapshotHandle':'h'},'deletionPolicy':'Delete','volumeSnapshotRef':{'name':'s','namespace':'default'}})))
 def test_content_ref(self):self.assertIn('CONTENT_REF',codes(obj('VolumeSnapshotContent','c',{'source':{'snapshotHandle':'h'},'deletionPolicy':'Retain'})))
 def test_static_valid(self):
  c=obj('VolumeSnapshotContent','c',{'source':{'snapshotHandle':'h'},'deletionPolicy':'Retain','volumeSnapshotRef':{'name':'s','namespace':'default'}})
  s=obj('VolumeSnapshot','s',{'source':{'volumeSnapshotContentName':'c'}})
  self.assertEqual(codes(c,s),[])
 def test_static_mismatch(self):
  c=obj('VolumeSnapshotContent','c',{'source':{'snapshotHandle':'h'},'deletionPolicy':'Retain','volumeSnapshotRef':{'name':'other','namespace':'default'}})
  s=obj('VolumeSnapshot','s',{'source':{'volumeSnapshotContentName':'c'}})
  self.assertIn('CONTENT_BINDING',codes(c,s))
 def test_restore_api_group(self):self.assertIn('RESTORE_GROUP',codes(obj('PersistentVolumeClaim','p',{'dataSource':{'kind':'VolumeSnapshot','name':'s','apiGroup':'bad'}})))
 def test_restore_missing_snapshot(self):self.assertIn('RESTORE_UNRESOLVED',codes(obj('PersistentVolumeClaim','p',{'dataSource':{'kind':'VolumeSnapshot','name':'s','apiGroup':'snapshot.storage.k8s.io'}})))
 def test_restore_mode(self):
  c=obj('VolumeSnapshotContent','c',{'source':{'snapshotHandle':'h'},'deletionPolicy':'Retain','sourceVolumeMode':'Block','volumeSnapshotRef':{'name':'s','namespace':'default'}})
  s=obj('VolumeSnapshot','s',{'source':{'volumeSnapshotContentName':'c'}})
  p=obj('PersistentVolumeClaim','p',{'dataSource':{'kind':'VolumeSnapshot','name':'s','apiGroup':'snapshot.storage.k8s.io'},'volumeMode':'Filesystem'})
  self.assertIn('RESTORE_MODE',codes(c,s,p))
 def test_duplicate(self):
  a=obj('VolumeSnapshot','s',{'source':{'persistentVolumeClaimName':'p'}});self.assertIn('DUPLICATE_OBJECT',codes(a,a))
 def test_missing_name(self):
  a=obj('VolumeSnapshot','s');a['metadata'].pop('name');self.assertIn('MISSING_NAME',codes(a))
 def test_cli_safe_and_strict(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'fixture.yml';p.write_text('apiVersion: snapshot.storage.k8s.io/v1\nkind: VolumeSnapshotClass\nmetadata:\n  name: c\ndriver: d\ndeletionPolicy: Retain\n')
   with redirect_stdout(StringIO()):self.assertEqual(audit.main([str(p),'--format','json']),0)
   p.write_text(p.read_text().replace('Retain','Delete'))
   with redirect_stdout(StringIO()):self.assertEqual(audit.main([str(p),'--strict']),2)
 def test_invalid_yaml(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'fixture.yml';p.write_text('kind: [')
   with redirect_stderr(StringIO()):self.assertEqual(audit.main([str(p)]),1)
if __name__=='__main__':unittest.main()
