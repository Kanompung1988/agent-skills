import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from scripts.audit import scan

DYNAMIC="ci-"+"$"+"{{ github.ref }}"

class ConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.dir=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def write(self,name,content):
        path=self.dir/name
        path.write_text(content,encoding="utf-8")
        return path
    def codes(self,*paths):
        result=scan(paths)
        self.assertEqual(result["errors"],[])
        return [f["code"] for f in result["findings"]]
    def test_dynamic_clean(self):
        self.assertEqual(self.codes(self.write("x.yml","concurrency:\n  group: "+DYNAMIC+"\n")),[])
    def test_dynamic_count(self):
        result=scan([self.write("x.yml","concurrency: "+DYNAMIC+"\n")])
        self.assertEqual(result["dynamic_groups_unresolved"],1)
    def test_missing_group(self):
        self.assertIn("CC001",self.codes(self.write("x.yml","concurrency: {cancel-in-progress: true}\n")))
    def test_empty_group(self):
        self.assertIn("CC001",self.codes(self.write("x.yml","concurrency: {group: ''}\n")))
    def test_invalid_shape(self):
        self.assertIn("CC001",self.codes(self.write("x.yml","concurrency: [one]\n")))
    def test_invalid_cancel(self):
        self.assertIn("CC004",self.codes(self.write("x.yml","concurrency: {group: x, cancel-in-progress: 8}\n")))
    def test_invalid_queue(self):
        self.assertIn("CC005",self.codes(self.write("x.yml","concurrency: {group: x, queue: wrong}\n")))
    def test_queue_max_cancel_conflict(self):
        self.assertIn("CC002",self.codes(self.write("x.yml","concurrency: {group: x, queue: max, cancel-in-progress: true}\n")))
    def test_release_cancellation(self):
        self.assertIn("CC003",self.codes(self.write("release.yml","concurrency: {group: x, cancel-in-progress: true}\n")))
    def test_job_cancellation(self):
        self.assertIn("CC003",self.codes(self.write("x.yml","jobs:\n  deploy:\n    concurrency: {group: x, cancel-in-progress: true}\n")))
    def test_nonrelease_cancellation(self):
        self.assertNotIn("CC003",self.codes(self.write("x.yml","concurrency: {group: x, cancel-in-progress: true}\n")))
    def test_literal_pending_queue(self):
        self.assertIn("CC006",self.codes(self.write("x.yml","concurrency: literal\n")))
    def test_queue_max_no_default_warning(self):
        self.assertNotIn("CC006",self.codes(self.write("x.yml","concurrency: {group: x, queue: max}\n")))
    def test_casefold_collision(self):
        a=self.write("one.yml","concurrency: PROD\n")
        b=self.write("two.yml","concurrency: prod\n")
        self.assertEqual(self.codes(a,b).count("CC007"),2)
    def test_no_collision(self):
        a=self.write("one.yml","concurrency: prodA\n")
        b=self.write("two.yml","concurrency: prodB\n")
        self.assertNotIn("CC007",self.codes(a,b))
    def test_workflow_and_job_collision(self):
        path=self.write("x.yml","concurrency: ci\njobs:\n  test:\n    concurrency: ci\n")
        self.assertEqual(self.codes(path).count("CC007"),2)
    def test_dynamic_not_claimed_collision(self):
        a=self.write("a.yml","concurrency: "+DYNAMIC+"\n")
        b=self.write("b.yml","concurrency: "+DYNAMIC+"\n")
        self.assertNotIn("CC007",self.codes(a,b))
    def test_bad_yaml(self):
        self.assertTrue(scan([self.write("x.yml","jobs: [oops\n")])["errors"])
    def test_empty_document(self):
        self.assertTrue(scan([self.write("x.yml","")])["errors"])
    def test_bad_jobs(self):
        self.assertTrue(scan([self.write("x.yml","jobs: nope\n")])["errors"])
    def test_missing_file(self):
        self.assertTrue(scan([self.dir/"missing.yml"])["errors"])
    def test_folder_scan(self):
        self.write("x.yaml","jobs: {}\n")
        self.assertEqual(scan([self.dir])["files_scanned"],1)
    def test_cli_clean(self):
        path=self.write("x.yml","concurrency: "+DYNAMIC+"\n")
        result=subprocess.run([sys.executable,"scripts/audit.py",str(path),"--json"],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual(json.loads(result.stdout)["findings"],[])
    def test_cli_review(self):
        path=self.write("x.yml","concurrency: prod\n")
        result=subprocess.run([sys.executable,"scripts/audit.py",str(path),"--json"],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertTrue(json.loads(result.stdout)["findings"])
    def test_cli_error(self):
        result=subprocess.run([sys.executable,"scripts/audit.py","not-found.yml","--json"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
