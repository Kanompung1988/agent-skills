import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit import audit,load,main,PREFIX

def namespace(name='x',labels=None,annotations=None):
    return {'kind':'Namespace','metadata':{'name':name,'labels':labels or {},'annotations':annotations or {}}}

def lbl(mode):return PREFIX+mode

def rules(doc,**kw):return {f['rule'] for f in audit([doc],**kw)}

class PSATests(unittest.TestCase):
    def test_safe(self):self.assertEqual(audit(load(ROOT/'fixtures/safe.yaml')),[])
    def test_review(self):self.assertTrue(audit(load(ROOT/'fixtures/review.yaml')))
    def test_missing_enforce(self):self.assertIn('MISSING_ENFORCE',rules(namespace()))
    def test_missing_no_minimum(self):self.assertEqual(rules(namespace(),minimum='none'),set())
    def test_weak_enforce(self):self.assertIn('WEAK_ENFORCE',rules(namespace(labels={lbl('enforce'):'baseline'}),minimum='restricted'))
    def test_baseline_allowed(self):self.assertEqual(rules(namespace(labels={lbl('enforce'):'baseline'})),set())
    def test_restricted_allowed(self):self.assertEqual(rules(namespace(labels={lbl('enforce'):'restricted'})),set())
    def test_privileged_review(self):self.assertIn('PRIVILEGED_ENFORCE',rules(namespace(labels={lbl('enforce'):'privileged'})))
    def test_invalid_level(self):self.assertIn('INVALID_LEVEL',rules(namespace(labels={lbl('enforce'):'unknown'})))
    def test_invalid_case(self):self.assertIn('INVALID_LEVEL',rules(namespace(labels={lbl('enforce'):'Restricted'})))
    def test_invalid_version(self):self.assertIn('INVALID_VERSION',rules(namespace(labels={lbl('enforce-version'):'1.37'})))
    def test_latest_version(self):self.assertNotIn('INVALID_VERSION',rules(namespace(labels={lbl('enforce-version'):'latest'})))
    def test_version_v1(self):self.assertNotIn('INVALID_VERSION',rules(namespace(labels={lbl('enforce-version'):'v1.37'})))
    def test_orphan_version(self):self.assertIn('ORPHAN_VERSION',rules(namespace(labels={lbl('warn-version'):'v1.37'})))
    def test_no_orphan_if_level(self):self.assertNotIn('ORPHAN_VERSION',rules(namespace(labels={lbl('warn-version'):'v1.37',lbl('warn'):'restricted'})))
    def test_unknown_label(self):self.assertIn('UNKNOWN_PSA_LABEL',rules(namespace(labels={lbl('enforce-foo'):'x'})))
    def test_annotations_not_labels(self):self.assertIn('PSA_ANNOTATION',rules(namespace(annotations={lbl('enforce'):'restricted'})))
    def test_unpinned_disabled(self):self.assertNotIn('UNPINNED_VERSION',rules(namespace(labels={lbl('enforce'):'baseline'})))
    def test_unpinned_enabled(self):self.assertIn('UNPINNED_VERSION',rules(namespace(labels={lbl('enforce'):'baseline'}),pin_versions=True))
    def test_pinned_works(self):self.assertNotIn('UNPINNED_VERSION',rules(namespace(labels={lbl('enforce'):'baseline',lbl('enforce-version'):'latest'}),pin_versions=True))
    def test_weaker_audit(self):self.assertIn('WEAKER_OBSERVABILITY',rules(namespace(labels={lbl('enforce'):'restricted',lbl('audit'):'baseline'})))
    def test_weaker_warn(self):self.assertIn('WEAKER_OBSERVABILITY',rules(namespace(labels={lbl('enforce'):'restricted',lbl('warn'):'baseline'})))
    def test_no_weaker_warn(self):self.assertNotIn('WEAKER_OBSERVABILITY',rules(namespace(labels={lbl('enforce'):'baseline',lbl('warn'):'restricted'})))
    def test_duplicates(self):self.assertIn('DUPLICATE_NAMESPACE',{x['rule'] for x in audit([namespace(),namespace()])})
    def test_exempt(self):self.assertEqual(audit([namespace('system')],exempt=['system']),[])
    def test_other_kinds_ignored(self):self.assertEqual(audit([{'kind':'Pod','metadata':{'name':'p'}}]),[])
    def test_invalid_metadata(self):
        with self.assertRaises(ValueError):audit([{'kind':'Namespace','metadata':'x'}])
    def test_missing_name(self):
        with self.assertRaises(ValueError):audit([{'kind':'Namespace','metadata':{}}])
    def test_invalid_labels(self):
        with self.assertRaises(ValueError):audit([{'kind':'Namespace','metadata':{'name':'x','labels':['a']}}])
    def test_duplicate_yaml_key(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.yaml';p.write_text('kind: Namespace\nkind: Namespace\n')
            with self.assertRaises(ValueError):load(p)
    def test_malformed_yaml_document(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.yaml';p.write_text('a list:\n- x\n- y\n---\nhello\n')
            with self.assertRaises(ValueError):load(p)
    def test_cli_safe(self):self.assertEqual(main([str(ROOT/'fixtures/safe.yaml'),'--format','json']),0)
    def test_cli_review(self):self.assertEqual(main([str(ROOT/'fixtures/review.yaml'),'--format','json']),2)
    def test_cli_missing(self):self.assertEqual(main([str(ROOT/'fixtures/missing.yaml')]),1)
    def test_subprocess(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/audit.py'),str(ROOT/'fixtures/review.yaml'),'--format','json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertIn('PRIVILEGED_ENFORCE',r.stdout)
    def test_deterministic(self):self.assertEqual(audit(load(ROOT/'fixtures/review.yaml')),audit(load(ROOT/'fixtures/review.yaml')))

if __name__=='__main__':unittest.main()
