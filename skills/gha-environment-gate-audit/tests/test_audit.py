import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.audit import audit, audit_document, environment_name, load_inventory, Yaml12Loader
import yaml

BASE={'environments':{'production':{'required_reviewers':2,'prevent_self_review':True,'can_admins_bypass':False,'deployment_branch_policy':{'protected_branches':True}}}}

class EnvironmentTests(unittest.TestCase):
    def test_yaml_on_not_boolean(self):
        self.assertIn('on',yaml.load('on: push\njobs: {}',Loader=Yaml12Loader))
    def test_yaml_true_is_boolean(self):
        self.assertIs(yaml.load('enabled: true',Loader=Yaml12Loader)['enabled'],True)
    def test_name_string(self): self.assertEqual(environment_name('production'),'production')
    def test_name_object(self): self.assertEqual(environment_name({'name':'production','url':'https://x'}),'production')
    def test_name_missing(self): self.assertIsNone(environment_name(None))
    def test_name_malformed(self): self.assertIsNone(environment_name({'url':'x'}))
    def test_no_deploy_empty(self): self.assertEqual(audit_document({'jobs':{'lint':{'runs-on':'ubuntu-latest'}}},'x',None),[])
    def test_deploy_missing_environment(self): self.assertEqual(audit_document({'jobs':{'deploy':{}}},'x',None)[0]['rule'],'ENV001')
    def test_env_without_inventory(self): self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',None)[0]['rule'],'ENV004')
    def test_case_insensitive_inventory(self):
        inv={'production':BASE['environments']['production']}
        self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'Production'}}},'x',inv),[])
    def test_missing_inventory(self): self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'prod'}}},'x',{})[0]['rule'],'ENV005')
    def test_dynamic_name(self): self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'${{ inputs.environment }}'}}},'x',{})[0]['rule'],'ENV003')
    def test_invalid_name(self): self.assertEqual(audit_document({'jobs':{'deploy':{'environment':{}}}},'x',{})[1]['rule'],'ENV002')
    def test_reviewers_empty(self): self.assertIn('ENV006',[x['rule'] for x in audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',{'production':{}})])
    def test_reviewer_boolean_not_integer(self):
        cfg={'production':dict(BASE['environments']['production'],required_reviewers=True)}
        self.assertIn('ENV006',[x['rule'] for x in audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',cfg)])
    def test_self_approval(self):
        cfg={'production':dict(BASE['environments']['production'],prevent_self_review=False)}
        self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',cfg)[0]['rule'],'ENV007')
    def test_admin_bypass(self):
        cfg={'production':dict(BASE['environments']['production'],can_admins_bypass=True)}
        self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',cfg)[0]['rule'],'ENV008')
    def test_branch_restriction(self):
        cfg={'production':dict(BASE['environments']['production'],deployment_branch_policy={})}
        self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',cfg)[0]['rule'],'ENV009')
    def test_custom_branch_policy(self):
        cfg={'production':dict(BASE['environments']['production'],deployment_branch_policy={'custom_branch_policies':True})}
        self.assertEqual(audit_document({'jobs':{'deploy':{'environment':'production'}}},'x',cfg),[])
    def test_non_deploy_job_known_env(self): self.assertEqual(audit_document({'jobs':{'verify':{'environment':'testing'}}},'x',{'testing':{}}),[])
    def test_invalid_jobs(self):
        with self.assertRaises(ValueError):audit_document({'jobs':[]},'x',{})
    def test_invalid_document(self):
        with self.assertRaises(ValueError):audit_document([],'x',{})
    def test_inventory_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'inventory.json';p.write_text('[]')
            with self.assertRaises(ValueError):load_inventory(p)
    def test_inventory_load(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'inventory.json';p.write_text(json.dumps(BASE))
            self.assertIn('production',load_inventory(p))
    def test_directory_scan(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'build.yml';p.write_text('on: push\njobs:\n  lint:\n    runs-on: ubuntu-latest\n')
            self.assertEqual(audit(Path(d))[0],1)
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):audit(Path(d))
    def test_cli_review(self):
        root=Path(__file__).resolve().parents[1]
        p=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/review.yml'),'--inventory',str(root/'examples/inventory.json'),'--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,1)
        self.assertGreater(len(json.loads(p.stdout)['findings']),0)
    def test_cli_safe(self):
        root=Path(__file__).resolve().parents[1]
        p=subprocess.run([sys.executable,str(root/'scripts/audit.py'),str(root/'examples/safe.yml'),'--inventory',str(root/'examples/inventory.json'),'--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_cli_missing_input(self):
        p=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'scripts/audit.py'),'/missing/nope','--json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)

if __name__=='__main__': unittest.main()
