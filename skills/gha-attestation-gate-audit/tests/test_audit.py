import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("audit", Path(__file__).parents[1] / "scripts" / "audit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def doc(steps=None, permissions=None):
    return {"permissions": permissions if permissions is not None else
            {"id-token": "write", "attestations": "write"},
            "jobs": {"build": {"steps": steps or []}}}


def rules(data):
    return {f["rule"] for f in mod.audit_workflow(data, "workflow.yml")}


class AttestationTests(unittest.TestCase):
    def test_empty_clean(self):
        self.assertEqual(rules(doc()), set())

    def test_good_attest(self):
        self.assertEqual(rules(doc([{"uses":"actions/attest@v4",
                                    "with":{"subject-path":"dist/*.whl"}}])), set())

    def test_missing_oidc(self):
        self.assertIn("AA001", rules(doc([{"uses":"actions/attest@v4",
                                            "with":{"subject-path":"file"}}],
                                           {"attestations":"write"})))

    def test_missing_attestations_write(self):
        self.assertIn("AA002", rules(doc([{"uses":"actions/attest@v4",
                                            "with":{"subject-path":"file"}}],
                                           {"id-token":"write"})))

    def test_job_override_permissions(self):
        data = doc([{"uses":"actions/attest@v4", "with":{"subject-path":"x"}}])
        data["jobs"]["build"]["permissions"]={"contents":"read"}
        self.assertEqual({"AA001","AA002"}, rules(data))

    def test_partial_subject_digest(self):
        self.assertIn("AA003", rules(doc([{"uses":"actions/attest@v4",
                                            "with":{"subject-digest":"sha256:abcd"}}])))

    def test_implicit_discovery(self):
        self.assertIn("AA004", rules(doc([{"uses":"actions/attest@v4"}])))

    def test_paired_image_subject(self):
        r=rules(doc([{"uses":"actions/attest@v4", "with":{
            "subject-name":"ghcr.io/org/demo","subject-digest":"sha256:abcdef"}}]))
        self.assertNotIn("AA003",r)
        self.assertNotIn("AA004",r)

    def test_verify_scope(self):
        self.assertIn("AA005", rules(doc([{"run":"gh attestation verify artifact"}])))

    def test_verify_scoped(self):
        self.assertNotIn("AA005",rules(doc([{"run":"gh attestation verify artifact -R org/repo"}])))

    def test_verify_owner(self):
        self.assertNotIn("AA005",rules(doc([{"run":"gh attestation verify artifact --owner org"}])))

    def test_fail_open(self):
        self.assertIn("AA007",rules(doc([{"run":"gh attestation verify a -R o/r || true"}])))

    def test_continue_on_error(self):
        self.assertIn("AA006",rules(doc([{"run":"gh attestation verify a -R o/r",
                                          "continue-on-error":True}])))

    def test_download_without_verify(self):
        self.assertIn("AA008",rules(doc([{"uses":"actions/download-artifact@v4"}])))

    def test_download_with_verify(self):
        self.assertNotIn("AA008",rules(doc([{"uses":"actions/download-artifact@v4"},
                                          {"run":"gh attestation verify a -R o/r"}])))

    def test_verify_order(self):
        self.assertIn("AA009",rules(doc([{"run":"gh attestation verify a -R o/r"},
                                         {"uses":"actions/download-artifact@v4"}])))

    def test_comment_is_not_verification(self):
        self.assertIn("AA008",rules(doc([{"uses":"actions/download-artifact@v4"},
                                         {"run":"# gh attestation verify artifact -R o/r"}])))

    def test_invalid_job(self):
        with self.assertRaises(ValueError):
            mod.audit_workflow({"jobs":{"x":"wrong"}},"x")

    def test_missing_jobs(self):
        with self.assertRaises(ValueError):
            mod.audit_workflow({},"x")

    def test_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"x.yml").write_text("jobs:\n  x:\n    steps: []\n")
            self.assertEqual(mod.audit_path(root)["count"],0)

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"file").write_text("jobs: {}\n")
            (root/"symlink").symlink_to("file")
            with self.assertRaises(ValueError):
                mod.audit_path(root/"symlink")

    def test_bad_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"bad.yml"
            f.write_text("jobs: [\n")
            with self.assertRaises(ValueError):
                mod.audit_path(f)


if __name__ == "__main__":
    unittest.main()
