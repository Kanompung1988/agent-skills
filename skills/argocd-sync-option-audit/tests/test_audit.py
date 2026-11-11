import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit

def app(*opts, **kw):
    spec={"syncPolicy":{"syncOptions":list(opts)}}
    spec.update(kw)
    return {"apiVersion":"argoproj.io/v1alpha1","kind":"Application","metadata":{"name":"demo"},"spec":spec}

def codes(doc):
    return {f["code"] for f in audit.review(doc)}

class SyncTests(unittest.TestCase):
    def test_clean(self): self.assertEqual(codes(app("ServerSideApply=true","FailOnSharedResource=true")),set())
    def test_replace(self): self.assertIn("AO003",codes(app("Replace=true")))
    def test_precedence(self): self.assertIn("AO004",codes(app("Replace=true","ServerSideApply=true")))
    def test_force(self): self.assertIn("AO005",codes(app("Force=true")))
    def test_validation_disabled(self): self.assertIn("AO006",codes(app("Validate=false")))
    def test_skip_dryrun(self): self.assertIn("AO007",codes(app("SkipDryRunOnMissingResource=true")))
    def test_no_prune(self): self.assertIn("AO008",codes(app("Prune=false")))
    def test_force_server_apply(self): self.assertIn("AO009",codes(app("Force=true","ServerSideApply=true")))
    def test_invalid_list(self): self.assertIn("AO001",codes(app("malformed")))
    def test_empty_entry(self): self.assertIn("AO001",codes(app("=true")))
    def test_conflicting_entries(self): self.assertIn("AO002",codes(app("Prune=true","Prune=false")))
    def test_automated_prune_empty(self):
        d=app()
        d["spec"]["syncPolicy"]["automated"]={"prune":True,"allowEmpty":True}
        self.assertIn("AO010",codes(d))
    def test_ignore_differences(self):
        self.assertIn("AO011",codes(app(ignoreDifferences=[{"group":"apps","kind":"Deployment"}])))
    def test_ignore_differences_respected(self):
        self.assertNotIn("AO011",codes(app("RespectIgnoreDifferences=true",ignoreDifferences=[{"kind":"Pod"}])))
    def test_annotation_force(self):
        d={"kind":"Job","metadata":{"name":"weekly","annotations":{"argocd.argoproj.io/sync-options":"Force=true, Replace=true"}}}
        self.assertIn("AO005",codes(d))
    def test_annotation_wrong_type(self):
        d={"kind":"Pod","metadata":{"annotations":{"argocd.argoproj.io/sync-options":["Force=true"]}}}
        self.assertIn("AO001",codes(d))
    def test_empty_annotations(self): self.assertEqual(codes({"kind":"Pod","metadata":{}}),set())
    def test_non_mapping(self): self.assertEqual(audit.review("bad"),[])
    def test_bad_metadata(self):
        with self.assertRaises(ValueError): audit.review({"kind":"Job","metadata":["bad"]})
    def test_safe_cli(self):
        with mock.patch("builtins.print"):
            self.assertEqual(audit.main([str(Path(__file__).resolve().parents[1]/"examples"/"safe.yaml"),"--json"]),0)
    def test_review_cli(self):
        with mock.patch("builtins.print"):
            self.assertEqual(audit.main([str(Path(__file__).resolve().parents[1]/"examples"/"review.yaml"),"--json"]),1)
    def test_invalid_yaml_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.yml";p.write_text("foo: [")
            with mock.patch("builtins.print"): self.assertEqual(audit.main([str(p)]),2)
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"target.yaml";p.write_text("kind: Pod")
            l=Path(d)/"link.yaml";l.symlink_to(p)
            with self.assertRaises(ValueError): audit.collect(l)
    def test_multi_document(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"docs.yaml";p.write_text("kind: Pod\n---\nkind: ConfigMap\n")
            self.assertEqual(audit.analyze(p)["documents_scanned"],2)
if __name__=="__main__":unittest.main()
