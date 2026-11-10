import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit

class Tests(unittest.TestCase):
    def codes(self, source):
        return [x["code"] for x in audit.analyze(source)]
    def test_safe_mount(self):
        self.assertEqual(self.codes("FROM alpine\nRUN --mount=type=secret,id=key,required=true cat /run/secrets/key\n"), [])
    def test_sensitive_arg(self):
        self.assertIn("BS001", self.codes("ARG API_TOKEN\n"))
    def test_sensitive_env(self):
        self.assertIn("BS002", self.codes("ENV DB_PASSWORD=foo\n"))
    def test_old_env(self):
        self.assertIn("BS002", self.codes("ENV SECRET_KEY foo\n"))
    def test_public_key_not_sensitive(self):
        self.assertEqual(self.codes("ENV PUBLIC_KEY=foo\n"), [])
    def test_regular_arg(self):
        self.assertEqual(self.codes("ARG BUILD_VERSION\n"), [])
    def test_optional_mount(self):
        self.assertIn("BS003", self.codes("RUN --mount=type=secret,id=key cat /run/secrets/key\n"))
    def test_required_mount(self):
        self.assertNotIn("BS003", self.codes("RUN --mount=type=secret,id=key,required=true true\n"))
    def test_empty_mount_identity(self):
        self.assertIn("BS004", self.codes("RUN --mount=type=secret true\n"))
    def test_explicit_target(self):
        self.assertNotIn("BS004", self.codes("RUN --mount=type=secret,target=/tmp/key,required=true cat /tmp/key\n"))
    def test_missing_same_run_mount(self):
        self.assertIn("BS005", self.codes("RUN cat /run/secrets/token\n"))
    def test_separate_run_not_persistent(self):
        self.assertIn("BS005", self.codes("RUN --mount=type=secret,id=token,required=true true\nRUN cat /run/secrets/token\n"))
    def test_arg_reference(self):
        self.assertIn("BS006", self.codes("ARG API_TOKEN\nRUN echo $API_TOKEN\n"))
    def test_env_reference(self):
        self.assertIn("BS006", self.codes("ENV SECRET_KEY=x\nRUN echo ${SECRET_KEY}\n"))
    def test_env_conflict(self):
        self.assertIn("BS007", self.codes("ENV API_TOKEN=x\nRUN --mount=type=secret,id=a,env=API_TOKEN,required=true true\n"))
    def test_comment_ignored(self):
        self.assertEqual(self.codes("# ARG PASSWORD\nFROM alpine\n"), [])
    def test_redaction(self):
        self.assertNotIn("supersecretvalue", str(audit.analyze("ENV API_TOKEN=supersecretvalue\n")))
    def test_continuation(self):
        result=list(audit.logical("RUN --mount=type=secret,id=a,required=true \\\n  cat /run/secrets/a\n"))
        self.assertEqual(result[0][0], 1)
        self.assertEqual(self.codes("RUN --mount=type=secret,id=a,required=true \\\n  cat /run/secrets/a\n"), [])
    def test_invalid_path(self):
        with self.assertRaises(ValueError): audit.scan("/absent/Dockerfile")
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"Dockerfile"
            p.write_text("FROM alpine")
            link=Path(tmp)/"link"
            link.symlink_to(p)
            with self.assertRaises(ValueError): audit.scan(link)
    def test_empty_input(self):
        self.assertEqual(self.codes(""), [])
    def test_named_target(self):
        self.assertNotIn("BS005", self.codes("RUN --mount=type=secret,target=/run/secrets/custom,required=true cat /run/secrets/custom\n"))
