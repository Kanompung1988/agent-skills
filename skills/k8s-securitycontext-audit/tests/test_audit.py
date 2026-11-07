import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit", ROOT / "scripts" / "audit.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)

BASE = {
 "apiVersion": "v1", "kind": "Pod", "metadata": {"name": "x"},
 "spec": {"securityContext": {"runAsNonRoot": True, "seccompProfile": {"type": "RuntimeDefault"}},
          "containers": [{"name": "web", "image": "example@sha256:123",
                          "securityContext": {"allowPrivilegeEscalation": False,
                           "capabilities": {"drop": ["ALL"]}, "readOnlyRootFilesystem": True}}]}
}

def run(doc):
    return [x["code"] for resource, spec in audit.pod_specs(doc) for x in audit.inspect_document(resource, spec)]

class TestSecurityContext(unittest.TestCase):
    def test_safe_pod(self): self.assertEqual(run(BASE), [])
    def test_untouched_container_detects_hardening(self):
        d = {"kind": "Pod", "metadata": {"name": "x"}, "spec": {"containers":[{"name":"x"}]}}
        self.assertTrue({"PRIVILEGE_ESCALATION","NONROOT_UNSET","CAPABILITIES_DROP","SECCOMP","WRITABLE_ROOT"} <= set(run(d)))
    def test_pod_inheritance(self):
        d = {**BASE, "spec": {**BASE["spec"], "containers": [{"name": "x", "securityContext":
            {"allowPrivilegeEscalation": False,"capabilities":{"drop":["ALL"]},"readOnlyRootFilesystem":True}}]}}
        self.assertEqual(run(d), [])
    def test_container_override_false(self):
        d = {**BASE, "spec": {**BASE["spec"], "containers": [{"name": "x", "securityContext":
            {"allowPrivilegeEscalation": False, "runAsNonRoot": False, "capabilities":{"drop":["ALL"]},
             "readOnlyRootFilesystem":True}}]}}
        self.assertIn("NONROOT_UNSET", run(d))
    def test_root_uid(self):
        d = {**BASE, "spec": {**BASE["spec"], "containers": [{"name": "x", "securityContext":{"runAsUser":0}}]}}
        self.assertIn("ROOT_UID", run(d))
    def test_privileged(self):
        d = {**BASE, "spec": {**BASE["spec"], "containers": [{"name":"x","securityContext":{"privileged":True}}]}}
        self.assertIn("PRIVILEGED", run(d))
    def test_capability_allowed(self):
        d = {**BASE, "spec": {**BASE["spec"], "containers":[{"name":"x","securityContext":
            {"allowPrivilegeEscalation":False,"capabilities":{"drop":["ALL"],"add":["NET_BIND_SERVICE"]},
             "readOnlyRootFilesystem":True}}]}}
        self.assertEqual(run(d), [])
    def test_capability_other(self):
        d = {**BASE, "spec": {**BASE["spec"], "containers":[{"name":"x","securityContext":
            {"capabilities":{"drop":["ALL"],"add":["SYS_ADMIN"]}}]}}
        self.assertIn("CAPABILITIES_ADD", run(d))
    def test_seccomp_unconfined(self):
        d = {**BASE, "spec": {**BASE["spec"], "securityContext":{"runAsNonRoot":True,"seccompProfile":{"type":"Unconfined"}}}}
        self.assertIn("SECCOMP", run(d))
    def test_windows_skips_linux_fields(self):
        d = {"kind":"Pod","spec":{"os":{"name":"windows"},"containers":[{"name":"x"}]}}
        self.assertEqual(run(d), [])
    def test_windows_hostprocess(self):
        d = {"kind":"Pod","spec":{"os":{"name":"windows"},
             "containers":[{"securityContext":{"windowsOptions":{"hostProcess":True}}}]}}
        self.assertIn("WINDOWS_HOST_PROCESS", run(d))
    def test_host_network(self):
        d = {**BASE,"spec":{**BASE["spec"],"hostNetwork":True}}
        self.assertIn("HOST_NETWORK", run(d))
    def test_host_pid(self):
        d = {**BASE,"spec":{**BASE["spec"],"hostPID":True}}
        self.assertIn("HOST_NAMESPACE", run(d))
    def test_deployment_template(self):
        d = {"kind":"Deployment","metadata":{"name":"d"},"spec":{"template":{"spec":BASE["spec"]}}}
        self.assertEqual(run(d), [])
    def test_cronjob(self):
        d = {"kind":"CronJob","spec":{"jobTemplate":{"spec":{"template":{"spec":BASE["spec"]}}}}}
        self.assertEqual(run(d), [])
    def test_list_of_documents(self):
        d = {"kind":"List","items":[BASE,{"kind":"ConfigMap","metadata":{"name":"ignored"}}]}
        self.assertEqual(run(d), [])
    def test_missing_spec_error(self):
        with self.assertRaises(ValueError): list(audit.pod_specs({"kind":"Pod"}))
    def test_wrong_container_type(self):
        with self.assertRaises(ValueError): audit.inspect_document("r",{"containers":"no"})
    def test_empty_containers_error(self):
        with self.assertRaises(ValueError): audit.inspect_document("r",{"containers":[]})
    def test_missing_file(self):
        with self.assertRaises(OSError): audit.audit("/invalid/nonexistent.yaml")
    def test_multi_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"x.yaml"
            path.write_text("kind: ConfigMap\n---\nkind: Pod\nspec:\n  containers:\n  - name: x\n")
            result=audit.audit(path)
            self.assertEqual(result["inspected"],1)
            self.assertGreater(result["count"],0)
    def test_nonmapping_doc(self):
        with self.assertRaises(ValueError): list(audit.pod_specs(["invalid"]))
    def test_yaml_parse_fails_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.yml"
            path.write_text("[bad")
            self.assertEqual(audit.main([str(path)]),2)

if __name__ == "__main__": unittest.main()
