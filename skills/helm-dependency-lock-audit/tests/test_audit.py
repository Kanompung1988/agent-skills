import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("audit",Path(__file__).resolve().parents[1]/"scripts"/"audit.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

DEP={"name":"redis","version":"18.1.0","repository":"https://charts.bitnami.com/bitnami"}
def chart(rows=None): return {"apiVersion":"v2","name":"app","version":"1.0.0","dependencies": rows if rows is not None else [DEP]}
def lock(rows=None): return {"dependencies": rows if rows is not None else [DEP], "digest":"sha256:abcde", "generated":"2026-11-16T00:00:00Z"}
def codes(ch,lk): return [r["code"] for r in audit.audit(ch,lk,"Chart.yaml")]

class HelmTests(unittest.TestCase):
    def test_clean(self): self.assertEqual(codes(chart(),lock()),[])
    def test_no_dependencies_no_lock(self): self.assertEqual(codes(chart([]),None),[])
    def test_missing_lock(self): self.assertIn("HL001",codes(chart(),None))
    def test_extra_lock_no_manifest(self): self.assertIn("HL005",codes(chart([]),lock()))
    def test_duplicate(self): self.assertIn("HL002",codes(chart([DEP,DEP]),lock()))
    def test_missing_entry(self): self.assertIn("HL003",codes(chart(),lock([])))
    def test_extra_entry(self): self.assertIn("HL004",codes(chart(),lock([DEP,DEP])))
    def test_repository_mismatch(self):
        changed=dict(DEP,repository="oci://different")
        c=codes(chart([changed]),lock()); self.assertIn("HL003",c); self.assertIn("HL004",c)
    def test_missing_name(self): self.assertIn("HL006",codes(chart([dict(DEP,name=None)]),lock()))
    def test_missing_version(self): self.assertIn("HL007",codes(chart([dict(DEP,version="")]),lock()))
    def test_missing_repository(self): self.assertIn("HL008",codes(chart([dict(DEP,repository="")]),lock()))
    def test_exact_version_mismatch(self): self.assertIn("HL009",codes(chart([dict(DEP,version="18.2.1")]),lock()))
    def test_range_version_does_not_false_alarm(self): self.assertNotIn("HL009",codes(chart([dict(DEP,version="^18.1.0")]),lock()))
    def test_missing_digest(self): self.assertIn("HL010",codes(chart(),dict(lock(),digest="")))
    def test_missing_generated(self): self.assertIn("HL011",codes(chart(),dict(lock(),generated=None)))
    def test_invalid_dependencies(self):
        with self.assertRaises(ValueError): audit.entries({"dependencies":"wrong"})
    def test_no_charts_dir(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): audit.run(d)
    def test_reads_chart(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/"Chart.yaml").write_text("apiVersion: v2\nname: app\nversion: 1.0.0\ndependencies: []\n")
            self.assertEqual(audit.run(d),[])
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/"Chart.yaml").write_text("name: a")
            q=p/"link.yaml"; q.symlink_to(p/"Chart.yaml")
            with self.assertRaises(ValueError): audit.read_yaml(q)
    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"Chart.yaml";p.write_text("foo: [broken")
            with self.assertRaises(ValueError): audit.read_yaml(p)

if __name__=="__main__": unittest.main()
