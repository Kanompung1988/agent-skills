import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('aud',root/'scripts/audit.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class Tests(unittest.TestCase):
    def audit(self,v,**settings):
        return mod.audit({'services':{'a':{'volumes':[v],**settings}}})
    def test_default_rw(self): self.assertEqual(self.audit('./x:/app')[0]['rule'],'CMW003')
    def test_short_ro(self): self.assertEqual(self.audit('./x:/app:ro'),[])
    def test_named_volume(self): self.assertEqual(self.audit('vol:/app'),[])
    def test_anonymous(self): self.assertEqual(self.audit('/app'),[])
    def test_root_host(self): self.assertEqual(self.audit('/:/host')[0]['rule'],'CMW002')
    def test_etc(self): self.assertEqual(self.audit('/etc:/app')[0]['rule'],'CMW002')
    def test_socket_ro(self): self.assertEqual(self.audit('/var/run/docker.sock:/sock:ro')[0]['rule'],'CMW001')
    def test_long_bind_rw(self): self.assertEqual(self.audit({'type':'bind','source':'./x','target':'/x'})[0]['rule'],'CMW003')
    def test_long_bind_ro(self): self.assertEqual(self.audit({'type':'bind','source':'./x','target':'/x','read_only':True}),[])
    def test_named_long(self): self.assertEqual(self.audit({'type':'volume','source':'data','target':'/x'}),[])
    def test_service_root_ro_not_bind_ro(self): self.assertEqual(self.audit('./x:/x',read_only=True)[0]['rule'],'CMW003')
    def test_interpolation(self): self.assertEqual(self.audit('$HOME/x:/x')[0]['rule'],'CMW005')
    def test_windows(self): self.assertEqual(self.audit('C:\\test:/app')[0]['rule'],'CMW005')
    def test_conflicting_flags(self): self.assertEqual(self.audit('./x:/x:rw,ro')[0]['rule'],'CMW005')
    def test_inherited(self): self.assertEqual(mod.audit({'services':{'web':{'volumes_from':['db']}}})[0]['rule'],'CMW006')
    def test_invalid_services(self):
        with self.assertRaises(ValueError): mod.audit({'services':[]})
    def test_invalid_volumes(self):
        with self.assertRaises(ValueError): mod.audit({'services':{'a':{'volumes':{}}}})
    def test_safe_fixture(self):
        x=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/safe.yml'),'--json'],capture_output=True,text=True)
        self.assertEqual(x.returncode,0,x.stderr);self.assertEqual(json.loads(x.stdout)['count'],0)
    def test_review_fixture(self):
        x=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/review.yml'),'--json'],capture_output=True,text=True)
        self.assertEqual(x.returncode,1,x.stderr);self.assertGreater(json.loads(x.stdout)['count'],0)
    def test_bad_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.yml';f.write_text('services: [')
            x=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(f)],capture_output=True)
            self.assertEqual(x.returncode,2)
