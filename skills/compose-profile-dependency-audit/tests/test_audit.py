import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit import audit, load, main, profile_set, dependencies

class ComposeProfileTests(unittest.TestCase):
    def test_safe(self): self.assertEqual(audit(load(ROOT/'fixtures/safe.yaml')), [])
    def test_default_disabled_dependency(self): self.assertIn('INACTIVE_DEPENDENCY',[f['rule'] for f in audit(load(ROOT/'fixtures/review.yaml'))])
    def test_profile_specific(self):
        fs=audit(load(ROOT/'fixtures/review.yaml'))
        self.assertTrue(any(x['scenario']=='profile:debug' and x['dependency']=='seed' for x in fs))
    def test_explicit_target_auto_profile(self):
        cfg={'services':{'one':{'profiles':['dev']},'two':{'depends_on':['one']}}}
        self.assertFalse(any(x['scenario']=='requested' for x in audit(cfg,target='one')))
    def test_explicit_target_incompatible(self):
        cfg={'services':{'one':{'profiles':['dev'],'depends_on':['two']},'two':{'profiles':['db']}}}
        self.assertTrue(any(x['scenario']=='requested' for x in audit(cfg,target='one')))
    def test_explicit_both_profiles(self):
        cfg={'services':{'one':{'profiles':['dev'],'depends_on':['two']},'two':{'profiles':['db']}}}
        self.assertFalse(any(x['scenario']=='requested' for x in audit(cfg,['db'],target='one')))
    def test_unknown_profile_error(self):
        with self.assertRaises(ValueError): audit({'services':{'x':{}}},['ghost'])
    def test_unknown_target(self):
        with self.assertRaises(ValueError): audit({'services':{'x':{}}},target='z')
    def test_unknown_dependency(self):
        x=audit({'services':{'x':{'depends_on':['missing']}}})
        self.assertEqual(x[0]['rule'],'UNKNOWN_SERVICE')
    def test_optional_dependency(self):
        self.assertEqual(audit({'services':{'x':{'depends_on':{'not-declared':{'required':False}}}}}),[])
    def test_networkmode_ref(self):
        self.assertTrue(any(x['rule']=='UNKNOWN_SERVICE' for x in audit({'services':{'x':{'network_mode':'service:db'}}})))
    def test_pid_ref(self):
        self.assertTrue(any(x['rule']=='UNKNOWN_SERVICE' for x in audit({'services':{'x':{'pid':'service:db'}}})))
    def test_ipc_ref(self):
        self.assertTrue(any(x['rule']=='UNKNOWN_SERVICE' for x in audit({'services':{'x':{'ipc':'service:db'}}})))
    def test_links_alias(self):
        self.assertEqual(audit({'services':{'x':{'links':['db:alias']},'db':{}}}),[])
    def test_extends_external_review(self):
        self.assertTrue(any(x['rule']=='EXTERNAL_EXTENDS' for x in audit({'services':{'x':{'extends':{'file':'base.yml','service':'base'}}}})))
    def test_extends_local(self):
        self.assertTrue(any(x['rule']=='UNKNOWN_SERVICE' for x in audit({'services':{'x':{'extends':'other'}}})))
    def test_dep_cycle(self):
        self.assertTrue(any(x['rule']=='DEPENDENCY_CYCLE' for x in audit({'services':{'a':{'depends_on':['b']},'b':{'depends_on':['a']}}})))
    def test_no_cycle(self): self.assertEqual(audit({'services':{'a':{'depends_on':['b']},'b':{}}}),[])
    def test_profile_format(self):
        with self.assertRaises(ValueError): profile_set({'profiles':['-bad']})
    def test_duplicate_profiles(self):
        with self.assertRaises(ValueError): profile_set({'profiles':['dev','dev']})
    def test_profile_not_list(self):
        with self.assertRaises(ValueError): profile_set({'profiles':'dev'})
    def test_invalid_dep(self):
        with self.assertRaises(ValueError): dependencies({'depends_on':True})
    def test_no_services(self):
        with self.assertRaises(ValueError): audit({'services':{}})
    def test_scalar_service(self):
        with self.assertRaises(ValueError): audit({'services':{'a':'x'}})
    def test_duplicate_yaml_key(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.yml';p.write_text('services:\n  a: {}\n  a: {}\n')
            with self.assertRaises(ValueError):load(p)
    def test_multiple_documents(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.yml';p.write_text('services: {a: {}}\n---\nservices: {b: {}}\n')
            with self.assertRaises(ValueError):load(p)
    def test_oversize(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.yml';p.write_text(' ' * 2000001)
            with self.assertRaises(ValueError):load(p)
    def test_cli_safe(self): self.assertEqual(main([str(ROOT/'fixtures/safe.yaml'),'--format','json']),0)
    def test_cli_review(self): self.assertEqual(main([str(ROOT/'fixtures/review.yaml'),'--format','json']),2)
    def test_cli_invalid(self): self.assertEqual(main([str(ROOT/'fixtures/none.yaml')]),1)
    def test_output_deterministic(self):
        x=load(ROOT/'fixtures/review.yaml');self.assertEqual(audit(x),audit(x))
    def test_actual_subprocess(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/audit.py'),str(ROOT/'fixtures/review.yaml'),'--format','json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertIn('INACTIVE_DEPENDENCY',r.stdout)

if __name__=='__main__':unittest.main()
