import importlib.util
from pathlib import Path
import tempfile
import unittest
path=Path(__file__).resolve().parents[1]/"scripts"/"audit.py"
spec=importlib.util.spec_from_file_location("tool",path)
tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)

def scan_yaml(contents):
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"workflow.yml"; p.write_text(contents)
        return tool.scan(p)

class AuditTests(unittest.TestCase):
    def test_trusted_write(self):
        self.assertEqual(scan_yaml("on: push\ncache-mode: write\njobs: {a: {}}\n"),[])
    def test_low_trust_default(self):
        self.assertEqual(scan_yaml("on: pull_request_target\njobs: {a: {}}\n"),[])
    def test_workflow_risky(self):
        self.assertEqual(scan_yaml("on: pull_request_target\ncache-mode: write\njobs: {a: {}}\n")[0]["rule"],"CACHE_WRITE_LOW_TRUST")
    def test_issue_event(self):
        self.assertEqual(scan_yaml("on: issue_comment\ncache-mode: write-only\njobs: {a: {}}\n")[0]["rule"],"CACHE_WRITE_LOW_TRUST")
    def test_job_override_read(self):
        self.assertEqual(scan_yaml("on: pull_request_target\ncache-mode: write\njobs: {a: {cache-mode: read}}\n"),[])
    def test_job_override_write(self):
        self.assertEqual(scan_yaml("on: pull_request_target\ncache-mode: read\njobs: {a: {cache-mode: write}}\n")[0]["rule"],"CACHE_WRITE_LOW_TRUST")
    def test_event_mapping(self):
        self.assertEqual(scan_yaml("on:\n  workflow_run:\n    workflows: [CI]\njobs: {a: {cache-mode: write}}\n")[0]["rule"],"CACHE_WRITE_LOW_TRUST")
    def test_event_list(self):
        self.assertEqual(scan_yaml("on: [push, issues]\njobs: {a: {cache-mode: write}}\n")[0]["rule"],"CACHE_WRITE_LOW_TRUST")
    def test_invalid_mode(self):
        self.assertEqual(scan_yaml("on: push\ncache-mode: x\njobs: {a: {}}\n")[0]["rule"],"CACHE_MODE_INVALID")
    def test_dynamic_mode(self):
        self.assertEqual(scan_yaml("on: push\ncache-mode: ${{ inputs.cache_mode }}\njobs: {a: {}}\n")[0]["rule"],"CACHE_MODE_DYNAMIC")
    def test_none_cache_step(self):
        s="on: push\ncache-mode: none\njobs:\n  a:\n    steps: [{uses: actions/cache@v4}]\n"
        self.assertEqual(scan_yaml(s)[0]["rule"],"CACHE_STEPS_DISABLED")
    def test_none_without_cache(self):
        self.assertEqual(scan_yaml("on: push\ncache-mode: none\njobs: {a: {}}\n"),[])
    def test_bad_yaml(self):
        with self.assertRaises(ValueError): scan_yaml("[")
    def test_invalid_jobs(self):
        with self.assertRaises(ValueError): scan_yaml("on: push\njobs: wrong\n")
    def test_multiple_yaml_docs(self):
        with self.assertRaises(ValueError): scan_yaml("on: push\njobs: {}\n---\non: push\n")
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/"src.yml"; src.write_text("on: push\njobs: {}\n")
            link=Path(d)/"link.yml"; link.symlink_to(src)
            with self.assertRaises(ValueError): tool.scan(link)
    def test_too_large(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"big.yml"; p.write_text(" "*(tool.LIMIT+1))
            with self.assertRaises(ValueError): tool.scan(p)
    def test_directory_filters_extensions(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"a.yaml").write_text("on: push\njobs: {}\n")
            (Path(d)/"b.txt").write_text("bad")
            self.assertEqual(tool.scan(Path(d)),[])
    def test_order(self):
        x=scan_yaml("on: issue_comment\ncache-mode: write\njobs: {z: {}, a: {}}\n")
        self.assertEqual([v["location"] for v in x],["jobs.a","jobs.z"])
    def test_nonmapping_root(self):
        with self.assertRaises(ValueError): scan_yaml("- value")
if __name__=="__main__": unittest.main()
