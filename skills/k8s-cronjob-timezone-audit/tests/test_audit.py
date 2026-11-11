import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit

def job(**settings):
    spec={"schedule": "0 9 * * *", "timeZone": "Etc/UTC", **settings}
    return {"kind": "CronJob", "metadata": {"name": "billing"}, "spec": spec}

class CronJobTests(unittest.TestCase):
    def codes(self, **settings):
        return {r["code"] for r in audit.review(job(**settings))}
    def test_clean(self): self.assertEqual(self.codes(), set())
    def test_missing_zone(self): self.assertIn("CJ003", self.codes(timeZone=None))
    def test_unknown_zone(self): self.assertIn("CJ004", self.codes(timeZone="Mars/Phobos"))
    def test_wrong_zone_type(self): self.assertIn("CJ004", self.codes(timeZone=55))
    def test_tz_in_schedule(self): self.assertIn("CJ002", self.codes(schedule="TZ=UTC 0 9 * * *"))
    def test_bad_schedule(self): self.assertIn("CJ001", self.codes(schedule="* * *"))
    def test_missing_schedule(self): self.assertIn("CJ001", self.codes(schedule=None))
    def test_deadline_too_short(self): self.assertIn("CJ007", self.codes(startingDeadlineSeconds=5))
    def test_deadline_acceptable(self): self.assertNotIn("CJ007", self.codes(startingDeadlineSeconds=15))
    def test_negative_deadline(self): self.assertIn("CJ006", self.codes(startingDeadlineSeconds=-1))
    def test_bool_deadline(self): self.assertIn("CJ006", self.codes(startingDeadlineSeconds=True))
    def test_replace(self): self.assertIn("CJ009", self.codes(concurrencyPolicy="Replace"))
    def test_forbid(self): self.assertIn("CJ010", self.codes(concurrencyPolicy="Forbid"))
    def test_invalid_policy(self): self.assertIn("CJ008", self.codes(concurrencyPolicy="bad"))
    def test_history_zero(self): self.assertIn("CJ011", self.codes(failedJobsHistoryLimit=0))
    def test_suspended(self): self.assertIn("CJ012", self.codes(suspend=True))
    def test_non_cron_ignored(self): self.assertEqual(audit.review({"kind": "Deployment"}), [])
    def test_dst_advice(self): self.assertIn("CJ005", self.codes(timeZone="America/New_York"))
    def test_document_resource(self):
        self.assertEqual(audit.review(job(suspend=True))[0]["resource"], "default/billing")
    def test_safe_cli(self):
        self.assertEqual(audit.main([str(Path(__file__).resolve().parents[1] / "examples" / "safe.yaml"), "--json"]), 0)
    def test_review_cli(self):
        with mock.patch("builtins.print"):
            self.assertEqual(audit.main([str(Path(__file__).resolve().parents[1] / "examples" / "review.yaml"), "--json"]), 1)
    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "bad.yaml"; p.write_text("foo: [")
            with mock.patch("builtins.print"):
                self.assertEqual(audit.main([str(p)]), 2)
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/"target.yaml"; target.write_text("kind: CronJob")
            link=Path(t)/"link.yaml"; link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                audit.collect(link)
    def test_multi_document(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"docs.yaml"; p.write_text("kind: Deployment\n---\nkind: CronJob\n")
            self.assertEqual(audit.analyze(p)["documents_scanned"],2)
    def test_malformed_spec(self):
        with self.assertRaises(ValueError):
            audit.review({"kind":"CronJob","spec":["not mapping"]})
if __name__=="__main__": unittest.main()
