import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from audit import audit_documents, audit_file

class RuntimeClassAuditTests(unittest.TestCase):
    def codes(self, name): return [x["rule"] for x in audit_file(Path(__file__).parents[1] / "fixtures" / name)]
    def test_safe_fixture_has_no_findings(self): self.assertEqual(self.codes("safe.yaml"), [])
    def test_node_selector_conflict_detected(self): self.assertIn("RUNTIMECLASS_NODESELECTOR_CONFLICT", self.codes("review.yaml"))
    def test_negative_overhead_rejected(self): self.assertIn("RUNTIMECLASS_OVERHEAD_QUANTITY_INVALID", self.codes("review.yaml"))
    def test_external_runtimeclass_is_info_not_error(self):
        f = [x for x in audit_file(Path(__file__).parents[1] / "fixtures/review.yaml") if x["rule"] == "RUNTIMECLASS_EXTERNAL_REFERENCE"]
        self.assertEqual(f[0]["severity"], "INFO")
    def test_missing_handler(self):
        c = [x["rule"] for x in audit_documents([{"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{}}])]
        self.assertIn("RUNTIMECLASS_HANDLER_REQUIRED", c)
    def test_missing_name(self):
        c = [x["rule"] for x in audit_documents([{"kind":"RuntimeClass","spec":{"handler":"x"}}])]
        self.assertIn("RUNTIMECLASS_NAME_REQUIRED", c)
    def test_duplicate_class(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x"}}
        c=[x["rule"] for x in audit_documents([obj,obj])]
        self.assertIn("RUNTIMECLASS_DUPLICATE", c)
    def test_selector_type_invalid(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":{"nodeSelector":["bad"]}}}
        c=[x["rule"] for x in audit_documents([obj])]
        self.assertIn("RUNTIMECLASS_NODESELECTOR_INVALID", c)
    def test_tolerations_type_invalid(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":{"tolerations":{}}}}
        c=[x["rule"] for x in audit_documents([obj])]
        self.assertIn("RUNTIMECLASS_TOLERATIONS_INVALID", c)
    def test_overhead_shape_invalid(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","overhead":{"podFixed":[]}}}
        c=[x["rule"] for x in audit_documents([obj])]
        self.assertIn("RUNTIMECLASS_OVERHEAD_INVALID", c)
    def test_overhead_bad_quantity(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","overhead":{"podFixed":{"cpu":"lots"}}}}
        c=[x["rule"] for x in audit_documents([obj])]
        self.assertIn("RUNTIMECLASS_OVERHEAD_QUANTITY_INVALID", c)
    def test_pod_selector_type_invalid(self):
        obj={"kind":"Pod","spec":{"runtimeClassName":"x","nodeSelector":["bad"]}}
        c=[x["rule"] for x in audit_documents([obj])]
        self.assertIn("POD_NODESELECTOR_INVALID", c)
    def test_statefulset_template_is_scanned(self):
        rc={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":{"nodeSelector":{"a":"b"}}}}
        ss={"kind":"StatefulSet","spec":{"template":{"spec":{"runtimeClassName":"x","nodeSelector":{"a":"c"}}}}}
        c=[x["rule"] for x in audit_documents([rc,ss])]
        self.assertIn("RUNTIMECLASS_NODESELECTOR_CONFLICT", c)
    def test_cronjob_template_is_scanned(self):
        rc={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":{"nodeSelector":{"a":"b"}}}}
        cj={"kind":"CronJob","spec":{"jobTemplate":{"spec":{"template":{"spec":{"runtimeClassName":"x","nodeSelector":{"a":"c"}}}}}}}
        c=[x["rule"] for x in audit_documents([rc,cj])]
        self.assertIn("RUNTIMECLASS_NODESELECTOR_CONFLICT", c)
    def test_podlist_is_scanned(self):
        obj={"kind":"PodList","items":[{"kind":"Pod","spec":{"runtimeClassName":"x"}}]}
        c=[x["rule"] for x in audit_documents([obj])]
        self.assertIn("RUNTIMECLASS_EXTERNAL_REFERENCE", c)
    def test_scheduling_shape_invalid(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":"bad"}}
        self.assertIn("RUNTIMECLASS_SCHEDULING_INVALID",[x["rule"] for x in audit_documents([obj])])
    def test_overhead_outer_shape_invalid(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","overhead":"bad"}}
        self.assertIn("RUNTIMECLASS_OVERHEAD_INVALID",[x["rule"] for x in audit_documents([obj])])
    def test_podtemplate_is_scanned(self):
        rc={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":{"nodeSelector":{"a":"b"}}}}
        tpl={"kind":"PodTemplate","template":{"spec":{"runtimeClassName":"x","nodeSelector":{"a":"c"}}}}
        self.assertIn("RUNTIMECLASS_NODESELECTOR_CONFLICT",[x["rule"] for x in audit_documents([rc,tpl])])
    def test_yaml_parse_error(self):
        p=Path(__file__).parents[1]/"fixtures"/"bad.yaml"; p.write_text("x: [\n",encoding="utf-8")
        try: self.assertIn("INPUT_PARSE_ERROR", self.codes("bad.yaml"))
        finally: p.unlink(missing_ok=True)
    def test_pod_without_runtimeclass_is_ignored(self):
        self.assertEqual(audit_documents([{"kind":"Pod","spec":{"runtimeClassName":"x"}}]), [])
    def test_runtimeclass_without_scheduling_is_valid(self):
        self.assertEqual(audit_documents([{"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x"}}]), [])
    def test_multiple_documents_preserve_document_number(self):
        fs=audit_documents([None,{"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{}}])
        self.assertTrue(all(x["document"]==2 for x in fs))
    def test_quantities_accept_binary_and_milli(self):
        obj={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","overhead":{"podFixed":{"cpu":"250m","memory":"64Mi"}}}}
        self.assertEqual(audit_documents([obj]), [])
    def test_selector_conflict_message_explains_admission(self):
        rc={"kind":"RuntimeClass","metadata":{"name":"x"},"spec":{"handler":"x","scheduling":{"nodeSelector":{"zone":"a"}}}}
        pod={"kind":"Pod","spec":{"runtimeClassName":"x","nodeSelector":{"zone":"b"}}}
        f=audit_documents([rc,pod])[0]
        self.assertIn("admission rejects", f["message"])

if __name__ == "__main__": unittest.main()
