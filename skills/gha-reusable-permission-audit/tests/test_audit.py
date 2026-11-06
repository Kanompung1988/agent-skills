import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('aud',root/'scripts/audit.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SHA='a'*40
def parse(s): return yaml.load(s,Loader=yaml.BaseLoader)
class Tests(unittest.TestCase):
    def check(self,ref,more='',top='permissions: read-all'):
        return mod.audit(parse('on: push\n'+top+'\njobs:\n  x:\n    uses: '+ref+'\n'+more))
    def rules(self,findings): return {x['rule'] for x in findings}
    def test_local(self): self.assertEqual(self.check('./.github/workflows/ci.yml'),[])
    def test_pinned(self): self.assertEqual(self.check('owner/repo/.github/workflows/ci.yml@'+SHA),[])
    def test_branch(self): self.assertIn('GRP001',self.rules(self.check('owner/repo/.github/workflows/ci.yml@main')))
    def test_tag(self): self.assertIn('GRP001',self.rules(self.check('owner/repo/.github/workflows/ci.yml@v1')))
    def test_secrets_inherit(self): self.assertIn('GRP002',self.rules(self.check('owner/repo/.github/workflows/ci.yml@'+SHA,'    secrets: inherit')))
    def test_local_secrets(self): self.assertNotIn('GRP002',self.rules(self.check('./.github/workflows/ci.yml','    secrets: inherit')))
    def test_explicit_secrets(self):
        f=self.check('owner/repo/.github/workflows/ci.yml@'+SHA,'    secrets:\n      token: some-variable')
        self.assertIn('GRP007',self.rules(f))
        self.assertNotIn('some-variable',json.dumps(f))
    def test_no_permissions(self): self.assertIn('GRP003',self.rules(self.check('./.github/workflows/ci.yml',top='name: CI')))
    def test_override(self): self.assertNotIn('GRP004',self.rules(self.check('./.github/workflows/ci.yml','    permissions: read-all',top='permissions: write-all')))
    def test_write_all(self): self.assertIn('GRP004',self.rules(self.check('./.github/workflows/ci.yml',top='permissions: write-all')))
    def test_write_scope(self): self.assertIn('GRP005',self.rules(self.check('./.github/workflows/ci.yml','    permissions:\n      contents: write')))
    def test_path_traversal(self): self.assertIn('GRP006',self.rules(self.check('./.github/workflows/../ci.yml')))
    def test_wrong_ref(self): self.assertIn('GRP006',self.rules(self.check('actions/checkout@v4')))
    def test_pr_target(self): self.assertIn('GRP008',self.rules(mod.audit(parse('on: pull_request_target\npermissions: write-all\njobs:\n  a:\n    uses: ./.github/workflows/a.yml'))))
    def test_nonreusable(self): self.assertEqual(mod.audit(parse('jobs:\n  a:\n    runs-on: ubuntu-latest')),[])
    def test_invalid_jobs(self):
        with self.assertRaises(ValueError): mod.audit({'jobs':[]})
    def test_fixture_safe(self):
        r=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/safe.yml'),'--json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['count'],0)
    def test_fixture_review(self):
        r=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/review.yml'),'--json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,1,r.stderr);self.assertGreater(json.loads(r.stdout)['count'],1)
    def test_bad_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.yml';p.write_text('jobs: [')
            r=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2)
