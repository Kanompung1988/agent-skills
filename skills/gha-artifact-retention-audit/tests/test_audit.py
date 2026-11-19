import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit', ROOT/'scripts/audit.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)


def workflow(days='none',uses='actions/upload-artifact@v4'):
    step={'uses':uses}
    if days!='none':step['with']={'retention-days':days}
    return {'jobs':{'build':{'runs-on':'ubuntu-latest','steps':[step]}}}


class RetentionTests(unittest.TestCase):
    def codes(self,doc,**opts):return [f['code'] for f in a.analyze_doc(doc,'ci.yml',**opts)]
    def test_safe_public(self): self.assertEqual([],self.codes(workflow(60),visibility='public'))
    def test_safe_private(self): self.assertEqual([],self.codes(workflow(300),visibility='private'))
    def test_public_cap(self):self.assertIn('OUT_OF_RANGE_RETENTION',self.codes(workflow(120),visibility='public'))
    def test_private_cap(self):self.assertIn('OUT_OF_RANGE_RETENTION',self.codes(workflow(450),visibility='private'))
    def test_unknown_cap(self):self.assertIn('OUT_OF_RANGE_RETENTION',self.codes(workflow(450)))
    def test_zero_is_default(self):self.assertEqual([],self.codes(workflow(0),visibility='public'))
    def test_missing_default(self):self.assertEqual([],self.codes(workflow(),visibility='public'))
    def test_negative(self):self.assertIn('OUT_OF_RANGE_RETENTION',self.codes(workflow(-1)))
    def test_bool_invalid(self):self.assertIn('INVALID_RETENTION',self.codes(workflow(True)))
    def test_string_numeric(self):self.assertEqual([],self.codes(workflow('30'),visibility='public'))
    def test_non_numeric(self):self.assertIn('INVALID_RETENTION',self.codes(workflow('n/a')))
    def test_dynamic_expr(self):self.assertIn('DYNAMIC_RETENTION',self.codes(workflow('${{ inputs.keep }}')))
    def test_policy_exceeded(self):self.assertIn('EXCEEDS_SUPPLIED_POLICY',self.codes(workflow(40),policy_days=30))
    def test_policy_satisfied(self):self.assertEqual([],self.codes(workflow(30),policy_days=30))
    def test_required_window(self):self.assertIn('BELOW_REQUIRED_WINDOW',self.codes(workflow(10),minimum_days=20))
    def test_required_window_satisfied(self):self.assertEqual([],self.codes(workflow(20),minimum_days=20))
    def test_default_unknown(self):self.assertIn('DEFAULT_RETENTION_UNKNOWN',self.codes(workflow(0),minimum_days=20))
    def test_default_policy_short(self):self.assertIn('DEFAULT_BELOW_REQUIRED_WINDOW',self.codes(workflow(),minimum_days=60,policy_days=30))
    def test_default_policy_long(self):self.assertEqual([],self.codes(workflow(),minimum_days=20,policy_days=30))
    def test_other_action_ignored(self):self.assertEqual([],self.codes(workflow(999,uses='actions/download-artifact@v4')))
    def test_fork_action_ignored(self):self.assertEqual([],self.codes(workflow(999,uses='attacker/upload-artifact@v4')))
    def test_nondict_doc(self):
        with self.assertRaises(ValueError): a.analyze_doc([], 'ci.yml')
    def test_bad_jobs(self):
        with self.assertRaises(ValueError): a.analyze_doc({'jobs':[]}, 'ci.yml')
    def test_unstructured_steps(self):self.assertIn('STEPS_UNRESOLVED',self.codes({'jobs':{'test':{'steps':'bad'}}}))
    def test_unstructured_with(self):self.assertIn('WITH_UNRESOLVED',self.codes({'jobs':{'test':{'steps':[{'uses':'actions/upload-artifact@v4','with':'bad'}]}}}))
    def test_safe_cli(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/audit.py'),str(ROOT/'fixtures/safe.yml'),'--visibility','public','--strict'],capture_output=True,text=True)
        self.assertEqual(0,p.returncode,p.stderr)
    def test_review_cli(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/audit.py'),str(ROOT/'fixtures/review.yml'),'--visibility','public','--format','json','--strict'],capture_output=True,text=True)
        self.assertEqual(2,p.returncode,p.stderr);self.assertGreaterEqual(json.loads(p.stdout)['count'],2)
    def test_missing_cli(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/audit.py'),'missing.yml'],capture_output=True,text=True)
        self.assertEqual(1,p.returncode)
    def test_directory_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'x.yml').write_text('jobs: {}');(p/'readme.txt').write_text('nothing')
            self.assertEqual([],a.collect([p]))
    def test_no_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):a.collect([Path(tmp)])

if __name__=='__main__':unittest.main()
