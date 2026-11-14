import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit import analyze, main, InputError

GOOD = """name: Release
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - run: npm publish
"""

class AuditTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        (self.root/".github/workflows").mkdir(parents=True)
        self.package={"name":"@acme/release","repository":"https://github.com/acme/release.git"}
        self.inventory={"repository":"acme/release","workflow":"release.yml"}
        self.workflow=GOOD
        self.write()
    def write(self):
        (self.root/"package.json").write_text(json.dumps(self.package))
        (self.root/"trusted-publisher.json").write_text(json.dumps(self.inventory))
        (self.root/".github/workflows/release.yml").write_text(self.workflow)
    def rules(self):
        self.write()
        return {f["rule"] for f in analyze(self.root)["findings"]}
    def test_safe(self): self.assertEqual(self.rules(),set())
    def test_cli_safe(self): self.assertEqual(main([str(self.root),"--json"]),0)
    def test_missing_oidc(self):
        self.workflow=self.workflow.replace("id-token: write","id-token: read")
        self.assertIn("NPM_ID_TOKEN_MISSING",self.rules())
    def test_missing_job_permissions(self):
        self.workflow=self.workflow.replace("    permissions:\n      contents: read\n      id-token: write\n","")
        self.assertIn("NPM_ID_TOKEN_MISSING",self.rules())
    def test_self_hosted(self):
        self.workflow=self.workflow.replace("ubuntu-latest","self-hosted")
        self.assertIn("NPM_UNSUPPORTED_RUNNER",self.rules())
    def test_dynamic_runner(self):
        self.workflow=self.workflow.replace("ubuntu-latest","$"+"{{ matrix.runner }}")
        self.assertIn("NPM_RUNNER_DYNAMIC",self.rules())
    def test_pull_request(self):
        self.workflow=self.workflow.replace("workflow_dispatch:","pull_request:")
        self.assertIn("NPM_PR_PUBLISH_TRIGGER",self.rules())
    def test_pull_request_target(self):
        self.workflow=self.workflow.replace("workflow_dispatch:","pull_request_target:")
        self.assertIn("NPM_PR_PUBLISH_TRIGGER",self.rules())
    def test_caller_identity(self):
        self.workflow=self.workflow.replace("workflow_dispatch:","workflow_call:")
        self.assertIn("NPM_CALLER_IDENTITY",self.rules())
    def test_token_fallback(self):
        self.workflow=self.workflow.replace("    steps:","    env:\n      NODE_AUTH_TOKEN: ignored\n    steps:")
        self.assertIn("NPM_TOKEN_FALLBACK",self.rules())
    def test_disabled_package_provenance(self):
        self.package["publishConfig"]={"provenance":False}
        self.assertIn("NPM_PROVENANCE_DISABLED",self.rules())
    def test_disabled_step_provenance(self):
        self.workflow=self.workflow.replace("npm publish","npm publish --provenance=false")
        self.assertIn("NPM_PROVENANCE_DISABLED",self.rules())
    def test_repository_mismatch(self):
        self.inventory["repository"]="wrong/repo"
        self.assertIn("NPM_REPOSITORY_MISMATCH",self.rules())
    def test_workflow_mismatch(self):
        self.inventory["workflow"]="different.yml"
        self.assertIn("NPM_WORKFLOW_MISMATCH",self.rules())
    def test_inventory_missing(self):
        self.write()
        (self.root/"trusted-publisher.json").unlink()
        self.assertIn("NPM_PUBLISHER_UNVERIFIED",{f["rule"] for f in analyze(self.root)["findings"]})
    def test_no_publish(self):
        self.workflow=self.workflow.replace("npm publish","npm ci")
        self.assertIn("NPM_NO_PUBLISH_JOB",self.rules())
    def test_invalid_yaml(self):
        self.workflow="["
        self.write()
        self.assertEqual(main([str(self.root),"--json"]),2)
    def test_invalid_json(self):
        self.write()
        (self.root/"package.json").write_text("{")
        self.assertEqual(main([str(self.root),"--json"]),2)
    def test_symlink_rejected(self):
        self.write()
        p=self.root/"package.json"
        p.unlink()
        p.symlink_to(self.root/"trusted-publisher.json")
        with self.assertRaises(InputError): analyze(self.root)
    def test_no_value_leak(self):
        self.workflow=self.workflow.replace("    steps:","    env:\n      NPM_TOKEN: private-value-sentinel\n    steps:")
        self.write()
        self.assertNotIn("private-value-sentinel",json.dumps(analyze(self.root)))

if __name__=="__main__":
    unittest.main()
