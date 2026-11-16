import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("audit", Path(__file__).resolve().parents[1] / "scripts" / "audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def template(**changes):
    c = dict(maxSkew=1, topologyKey="topology.kubernetes.io/zone", whenUnsatisfiable="DoNotSchedule",
             labelSelector={"matchLabels": {"app": "api"}})
    c.update(changes)
    return {"kind": "Deployment", "metadata": {"name": "api"},
            "spec": {"template": {"metadata": {"labels": {"app": "api"}},
                                  "spec": {"topologySpreadConstraints": [c]}}}}


def codes(obj):
    return [x["code"] for x in audit.audit_documents([obj])]


class TopologyAuditTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(codes(template()), [])
    def test_min_domains_ok(self): self.assertEqual(codes(template(minDomains=3)), [])
    def test_skew_zero(self): self.assertIn("TS001", codes(template(maxSkew=0)))
    def test_boolean_skew(self): self.assertIn("TS001", codes(template(maxSkew=True)))
    def test_bad_topology(self): self.assertIn("TS002", codes(template(topologyKey="")))
    def test_bad_mode(self): self.assertIn("TS003", codes(template(whenUnsatisfiable="Never")))
    def test_min_domains_schedule(self): self.assertIn("TS004", codes(template(minDomains=2, whenUnsatisfiable="ScheduleAnyway")))
    def test_min_domains_zero(self): self.assertIn("TS004", codes(template(minDomains=0)))
    def test_bad_affinity(self): self.assertIn("TS005", codes(template(nodeAffinityPolicy="Unknown")))
    def test_bad_taints(self): self.assertIn("TS005", codes(template(nodeTaintsPolicy="Unknown")))
    def test_match_keys_missing_selector(self): self.assertIn("TS006", codes(template(labelSelector=None, matchLabelKeys=["app"])))
    def test_match_keys_clash(self): self.assertIn("TS007", codes(template(matchLabelKeys=["app"])))
    def test_match_keys_absent(self): self.assertIn("TS008", codes(template(matchLabelKeys=["revision"])))
    def test_missing_selector_review(self): self.assertIn("TS009", codes(template(labelSelector=None)))
    def test_bad_operator(self): self.assertIn("TS010", codes(template(labelSelector={"matchExpressions": [{"key":"app", "operator":"Oops"}]})))
    def test_selector_no_self_match(self): self.assertIn("TS011", codes(template(labelSelector={"matchLabels":{"app":"other"}})))
    def test_expressions_match(self): self.assertEqual(codes(template(labelSelector={"matchExpressions":[{"key":"app","operator":"In","values":["api"]}]})), [])
    def test_expressions_existence(self): self.assertEqual(codes(template(labelSelector={"matchExpressions":[{"key":"app","operator":"Exists"}]})), [])
    def test_duplicates(self):
        doc=template()
        first=doc["spec"]["template"]["spec"]["topologySpreadConstraints"][0]
        doc["spec"]["template"]["spec"]["topologySpreadConstraints"].append(dict(first))
        self.assertIn("TS012", codes(doc))
    def test_pod_root(self):
        o={"kind":"Pod","metadata":{"name":"x","labels":{"app":"api"}},"spec":{"topologySpreadConstraints":[template()["spec"]["template"]["spec"]["topologySpreadConstraints"][0]]}}
        self.assertEqual(codes(o), [])
    def test_cronjob_nested(self):
        t=template()["spec"]["template"]
        o={"kind":"CronJob","spec":{"jobTemplate":{"spec":{"template":t}}}}
        self.assertEqual(codes(o), [])
    def test_unsupported_kind(self): self.assertEqual(codes({"kind":"Service"}), [])
    def test_cli_empty_dir(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): audit.run(d)
    def test_cli_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"review.yaml"
            p.write_text("kind: Deployment\\nmetadata: {name: demo}\\nspec: {template: {metadata: {labels: {app: api}}, spec: {topologySpreadConstraints: [{maxSkew: 0, topologyKey: ''}]}}}\\n".replace("\\n","\n"))
            self.assertGreaterEqual(len(audit.run(p)),2)


if __name__ == "__main__": unittest.main()
