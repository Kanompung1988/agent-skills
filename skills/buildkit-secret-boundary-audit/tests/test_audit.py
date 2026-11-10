import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from scripts.audit import scan, parse, instructions

class BuildSecretTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.dir=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def file(self,content,name="Dockerfile"):
        p=self.dir/name
        p.write_text(content,encoding="utf-8")
        return p
    def codes(self,text):
        result=scan([self.file(text)])
        self.assertEqual(result["errors"],[])
        return [f["code"] for f in result["findings"]]
    def test_safe_build(self):
        self.assertEqual(self.codes("FROM alpine\nRUN --mount=type=secret,id=token,required=true cat /run/secrets/token\nCOPY src/ /app/\n"),[])
    def test_arg_secret(self):
        self.assertIn("BK002",self.codes("FROM alpine\nARG API_TOKEN\n"))
    def test_arg_default_secret(self):
        self.assertIn("BK002",self.codes("ARG DB_PASSWORD=unused\n"))
    def test_env_secret(self):
        self.assertIn("BK002",self.codes("ENV API_KEY=example\n"))
    def test_env_space_syntax(self):
        self.assertIn("BK002",self.codes("ENV AUTH_TOKEN value\n"))
    def test_normal_arg(self):
        self.assertNotIn("BK002",self.codes("ARG BUILD_VERSION=1\n"))
    def test_unparseable_arg(self):
        self.assertIn("BK001",self.codes('ARG API_TOKEN="unterminated\n'))
    def test_run_secret_env(self):
        self.assertIn("BK005",self.codes("RUN curl -H $API_TOKEN example.invalid\n"))
    def test_run_without_secret_variable(self):
        self.assertNotIn("BK005",self.codes("RUN echo hello\n"))
    def test_run_secret_mount_prevents_bk005(self):
        self.assertNotIn("BK005",self.codes("RUN --mount=type=secret,id=token,required=true echo $API_TOKEN\n"))
    def test_optional_mount(self):
        self.assertIn("BK004",self.codes("RUN --mount=type=secret,id=token cat /run/secrets/token\n"))
    def test_required_mount(self):
        self.assertNotIn("BK004",self.codes("RUN --mount=type=secret,id=token,required=true echo ok\n"))
    def test_missing_id_and_target(self):
        self.assertIn("BK003",self.codes("RUN --mount=type=secret echo ok\n"))
    def test_target_only_allowed(self):
        self.assertNotIn("BK003",self.codes("RUN --mount=type=secret,target=/secret,required=true cat /secret\n"))
    def test_copy_npmrc(self):
        self.assertIn("BK006",self.codes("COPY .npmrc /root/.npmrc\n"))
    def test_copy_source(self):
        self.assertNotIn("BK006",self.codes("COPY src/ /app/\n"))
    def test_add_password_in_url(self):
        self.assertIn("BK007",self.codes("ADD https://name:password@invalid.example/a /tmp/a\n"))
    def test_add_normal_url(self):
        self.assertNotIn("BK007",self.codes("ADD https://invalid.example/a /tmp/a\n"))
    def test_continuation_lines(self):
        rows=list(instructions("RUN --mount=type=secret,id=token,\\\n    required=true echo ok\n"))
        self.assertEqual(rows[0][0],1)
        self.assertIn("required=true",rows[0][1])
    def test_unsupported_escape(self):
        self.assertTrue(parse(self.file("# escape="+chr(96)+"\nFROM alpine\n"))[1])
    def test_missing_file(self):
        self.assertTrue(scan([self.dir/"missing"])["errors"])
    def test_directory(self):
        self.file("FROM alpine\n",name="Dockerfile.test")
        self.assertEqual(scan([self.dir])["files_scanned"],1)
    def test_no_secret_values_in_findings(self):
        output=scan([self.file("ENV API_KEY=very-private-value\n")])
        self.assertNotIn("very-private-value",json.dumps(output))
    def test_cli_safe(self):
        p=self.file("FROM alpine\nRUN --mount=type=secret,id=token,required=true cat /run/secrets/token\n")
        r=subprocess.run([sys.executable,"scripts/audit.py",str(p),"--json"],capture_output=True,text=True)
        self.assertEqual(r.returncode,0)
    def test_cli_review(self):
        p=self.file("ARG API_TOKEN\n")
        r=subprocess.run([sys.executable,"scripts/audit.py",str(p),"--json"],capture_output=True,text=True)
        self.assertEqual(r.returncode,1)
        self.assertTrue(json.loads(r.stdout)["findings"])
    def test_cli_missing(self):
        r=subprocess.run([sys.executable,"scripts/audit.py","missing-file","--json"],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
