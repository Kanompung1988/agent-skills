import importlib.util
from pathlib import Path
import tempfile
import unittest
src=Path(__file__).resolve().parents[1]/"scripts"/"audit.py"
spec=importlib.util.spec_from_file_location("tool",src)
tool=importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)

BASE="""apiVersion: apps/v1
kind: StatefulSet
metadata: {name: db, namespace: prod}
spec:
  volumeClaimTemplates:
    - metadata: {name: data}
      spec: {resources: {requests: {storage: 2Gi}}}
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain
    whenScaled: Retain
"""
def scan_yaml(s):
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"sts.yml"; p.write_text(s)
        return tool.scan(p)

class AuditTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(scan_yaml(BASE),[])
    def test_default_retain(self):
        self.assertEqual(scan_yaml(BASE.split("  persistentVolumeClaimRetentionPolicy:")[0]),[])
    def test_delete_set(self):
        x=scan_yaml(BASE.replace("whenDeleted: Retain","whenDeleted: Delete"))
        self.assertEqual(x[0]["rule"],"PVC_DELETE_ON_SET_REMOVAL")
    def test_delete_scale(self):
        x=scan_yaml(BASE.replace("whenScaled: Retain","whenScaled: Delete"))
        self.assertEqual(x[0]["rule"],"PVC_DELETE_ON_SCALE_DOWN")
    def test_two_delete(self):
        self.assertEqual(len(scan_yaml(BASE.replace(": Retain",": Delete"))),2)
    def test_invalid_value(self):
        self.assertEqual(scan_yaml(BASE.replace("whenScaled: Retain","whenScaled: Never"))[0]["rule"],"PVC_POLICY_INVALID_VALUE")
    def test_unknown_field(self):
        self.assertEqual(scan_yaml(BASE.replace("whenScaled: Retain","whenScale: Delete"))[0]["rule"],"PVC_POLICY_UNKNOWN_FIELD")
    def test_null_policy(self):
        s=BASE.split("  persistentVolumeClaimRetentionPolicy:")[0]+"  persistentVolumeClaimRetentionPolicy:\n"
        self.assertEqual(scan_yaml(s)[0]["rule"],"PVC_POLICY_MALFORMED")
    def test_duplicate_template(self):
        s=BASE.replace("  persistentVolumeClaimRetentionPolicy:","    - metadata: {name: data}\n      spec: {resources: {requests: {storage: 2Gi}}}\n  persistentVolumeClaimRetentionPolicy:")
        self.assertIn("PVC_TEMPLATE_DUPLICATE",[x["rule"] for x in scan_yaml(s)])
    def test_unnamed_template(self):
        self.assertEqual(scan_yaml(BASE.replace("name: data","some: data"))[0]["rule"],"PVC_TEMPLATE_UNNAMED")
    def test_missing_storage(self):
        self.assertEqual(scan_yaml(BASE.replace("requests: {storage: 2Gi}","requests: {}"))[0]["rule"],"PVC_STORAGE_REQUEST_MISSING")
    def test_non_mapping_template(self):
        s=BASE.replace("    - metadata: {name: data}\n      spec: {resources: {requests: {storage: 2Gi}}}","    - no")
        self.assertEqual(scan_yaml(s)[0]["rule"],"PVC_TEMPLATE_INVALID")
    def test_without_claims(self):
        s=BASE.split("  volumeClaimTemplates:")[0]+"  persistentVolumeClaimRetentionPolicy: {whenDeleted: Delete}\n"
        self.assertEqual(scan_yaml(s)[0]["rule"],"PVC_POLICY_WITHOUT_TEMPLATES")
    def test_ignore_deployment(self):
        self.assertEqual(scan_yaml(BASE.replace("kind: StatefulSet","kind: Deployment")),[])
    def test_version_review(self):
        self.assertEqual(scan_yaml(BASE.replace("apiVersion: apps/v1","apiVersion: apps/v1beta1"))[0]["rule"],"STS_VERSION_REVIEW")
    def test_namespace(self):
        self.assertEqual(scan_yaml(BASE.replace("whenScaled: Retain","whenScaled: Delete"))[0]["namespace"],"prod")
    def test_multi_document(self):
        self.assertEqual(scan_yaml("kind: Service\n---\n"+BASE),[])
    def test_invalid_yaml(self):
        with self.assertRaises(ValueError): scan_yaml("[")
    def test_invalid_spec(self):
        with self.assertRaises(ValueError): scan_yaml("kind: StatefulSet\nspec: wrong")
    def test_invalid_templates(self):
        with self.assertRaises(ValueError): scan_yaml("kind: StatefulSet\nspec: {volumeClaimTemplates: wrong}")
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"s.yaml"; p.write_text(BASE)
            link=Path(d)/"l.yaml"; link.symlink_to(p)
            with self.assertRaises(ValueError): tool.scan(link)
    def test_limit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"big.yaml"; p.write_text(" "*(tool.LIMIT+1))
            with self.assertRaises(ValueError): tool.scan(p)
    def test_order(self):
        x=scan_yaml(BASE.replace(": Retain",": Delete"))
        self.assertEqual([i["rule"] for i in x],sorted(i["rule"] for i in x))
    def test_empty_document(self):
        self.assertEqual(scan_yaml("---\n"),[])
if __name__=="__main__": unittest.main()
