import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit

class Tests(unittest.TestCase):
    def codes(self, yml):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "workflow.yml"
            p.write_text(yml)
            return [f["code"] for f in audit.scan(p)]
    def test_safe(self):
        self.assertEqual(self.codes("concurrency:\n  group: ${{ github.workflow }}-${{ github.ref }}\n"), [])
    def test_missing_group(self):
        self.assertIn("CC001", self.codes("concurrency:\n  group: ''\n"))
    def test_invalid_structure(self):
        self.assertIn("CC001", self.codes("concurrency: [a, b]\n"))
    def test_queue_conflict(self):
        self.assertIn("CC002", self.codes("concurrency:\n  group: fixed\n  queue: max\n  cancel-in-progress: true\n"))
    def test_head_ref_push(self):
        self.assertIn("CC003", self.codes("on: push\nconcurrency:\n  group: ${{ github.head_ref }}\n"))
    def test_head_ref_fallback(self):
        self.assertNotIn("CC003", self.codes("on: push\nconcurrency:\n  group: ${{ github.head_ref || github.run_id }}\n"))
    def test_release_cancellation(self):
        self.assertIn("CC004", self.codes("name: Release\nconcurrency:\n  group: publish\n  cancel-in-progress: true\n"))
    def test_global_ref_only(self):
        self.assertIn("CC005", self.codes("concurrency:\n  group: ${{ github.ref }}\n"))
    def test_cancel_invalid(self):
        self.assertIn("CC006", self.codes("concurrency:\n  group: fixed\n  cancel-in-progress: maybe\n"))
    def test_queue_invalid(self):
        self.assertIn("CC007", self.codes("concurrency:\n  group: fixed\n  queue: all\n"))
    def test_job_collision(self):
        self.assertIn("CC009", self.codes("jobs:\n  a:\n    concurrency: fixed\n  b:\n    concurrency: FIXED\n"))
    def test_workflow_job_collision(self):
        self.assertIn("CC009", self.codes("concurrency: fixed\njobs:\n  a:\n    concurrency: fixed\n"))
    def test_cross_file_collision(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.yml").write_text("concurrency: Prod\n")
            (Path(d) / "b.yml").write_text("concurrency: prod\n")
            self.assertEqual([x["code"] for x in audit.scan(d)], ["CC008", "CC008"])
    def test_case_normalization(self):
        self.assertEqual(audit.normalize("PrOd"), "prod")
    def test_expression_spacing(self):
        self.assertEqual(audit.normalize("${{  github.ref  }}"), "${{ github.ref }}")
    def test_missing_input(self):
        with self.assertRaises(ValueError): audit.scan("/missing/path")
    def test_no_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): audit.scan(d)
    def test_non_mapping(self):
        with self.assertRaises(ValueError): audit.analyze({Path("x.yml"): []})
    def test_bad_jobs(self):
        with self.assertRaises(ValueError): audit.analyze({Path("x.yml"): {"jobs": []}})
    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d) / "x.yml"
            p.write_text(": : invalid")
            with self.assertRaises(Exception): audit.scan(p)
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d) / "x.yml"
            p.write_text("{}")
            q=Path(d) / "link.yml"
            q.symlink_to(p)
            with self.assertRaises(ValueError): audit.scan(q)
