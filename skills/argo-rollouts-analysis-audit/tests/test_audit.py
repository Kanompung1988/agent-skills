"""Unit tests for Argo metric and template contract checks."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit


def res(kind, spec=None, name="test", ns="default"):
    return {"apiVersion": "argoproj.io/v1alpha1", "kind": kind,
            "metadata": {"name": name, "namespace": ns}, "spec": spec or {}}


def metric(**kwargs):
    return dict({"name": "rate", "provider": {"prometheus": {"query": "up"}},
                 "successCondition": "result[0] >= 0.95"}, **kwargs)


def template(metrics=None, name="gate", ns="default", kind="AnalysisTemplate", args=None):
    return res(kind, {"metrics": metrics if metrics is not None else [metric()],
                      "args": args or []}, name, ns)


def rollout(name="gate", ns="default", cluster=False, args=None):
    ref = {"templateName": name}
    if cluster:
        ref["clusterScope"] = True
    return res("Rollout", {"strategy": {"canary": {"analysis": {
        "templates": [ref], "args": args or []}, "steps": [{"setWeight": 10}]}}}, ns=ns)


def audit(*resources):
    return __import__("audit").audit([("examples.yaml", r) for r in resources])


class MetricContracts(unittest.TestCase):
    def test_good_template(self):
        self.assertEqual(audit(template()), [])
    def test_missing_conditions(self):
        m = metric()
        del m["successCondition"]
        self.assertIn("AR001", {f["code"] for f in audit(template([m]))})
    def test_explicit_failure_only_valid(self):
        m = metric()
        del m["successCondition"]
        m["failureCondition"] = "result[0] < 0.5"
        self.assertEqual(audit(template([m])), [])
    def test_failure_disabled_without_success(self):
        self.assertIn("AR002", {f["code"] for f in audit(template([metric(failureLimit=-1)]))})
    def test_failure_disabled_with_consecutive_success(self):
        self.assertEqual(audit(template([metric(failureLimit=-1, consecutiveSuccessLimit=3)])), [])
    def test_negative_failure_limit_invalid(self):
        self.assertIn("AR003", {f["code"] for f in audit(template([metric(failureLimit=-2)]))})
    def test_negative_consecutive_invalid(self):
        self.assertIn("AR003", {f["code"] for f in audit(template([metric(consecutiveSuccessLimit=-1)]))})
    def test_bool_limit_invalid(self):
        self.assertIn("AR003", {f["code"] for f in audit(template([metric(failureLimit=True)]))})
    def test_zero_count_valid_for_background(self):
        self.assertEqual(audit(template([metric(count=0)])), [])
    def test_negative_count_invalid(self):
        self.assertIn("AR005", {f["code"] for f in audit(template([metric(count=-2)]))})
    def test_valid_count(self):
        self.assertEqual(audit(template([metric(count=4)])), [])
    def test_missing_provider(self):
        m = metric()
        del m["provider"]
        self.assertIn("AR004", {f["code"] for f in audit(template([m]))})
    def test_two_providers_invalid(self):
        m = metric()
        m["provider"]["web"] = {"url": "https://invalid"}
        self.assertIn("AR004", {f["code"] for f in audit(template([m]))})
    def test_duplicate_metric(self):
        self.assertIn("AR006", {f["code"] for f in audit(template([metric(), metric()]))})
    def test_no_metric_name(self):
        m = metric()
        del m["name"]
        self.assertIn("AR009", {f["code"] for f in audit(template([m]))})
    def test_blank_condition(self):
        self.assertIn("AR010", {f["code"] for f in audit(template([metric(successCondition="  ")]))})
    def test_empty_template(self):
        self.assertIn("AR012", {f["code"] for f in audit(template([]))})
    def test_duplicate_template_identity(self):
        self.assertIn("AR011", {f["code"] for f in audit(template(), template())})


class ReferenceContracts(unittest.TestCase):
    def test_missing_local_template(self):
        self.assertIn("AR007", {f["code"] for f in audit(rollout())})
    def test_matching_template(self):
        self.assertEqual(audit(rollout(), template()), [])
    def test_wrong_namespace_not_matched(self):
        self.assertIn("AR007", {f["code"] for f in audit(rollout(ns="other"), template())})
    def test_cluster_template_scope(self):
        self.assertEqual(audit(rollout(cluster=True), template(kind="ClusterAnalysisTemplate")), [])
    def test_cluster_template_not_local(self):
        self.assertIn("AR007", {f["code"] for f in audit(rollout(cluster=True), template())})
    def test_required_arg_missing(self):
        t = template(args=[{"name": "service-name"}])
        self.assertIn("AR008", {f["code"] for f in audit(rollout(), t)})
    def test_required_arg_supplied(self):
        t = template(args=[{"name": "service-name"}])
        self.assertEqual(audit(rollout(args=[{"name": "service-name", "value": "svc"}]), t), [])
    def test_defaulted_arg_not_required(self):
        t = template(args=[{"name": "service-name", "value": "fallback"}])
        self.assertEqual(audit(rollout(), t), [])
    def test_missing_template_name(self):
        r = rollout()
        r["spec"]["strategy"]["canary"]["analysis"]["templates"] = [{}]
        self.assertIn("AR014", {f["code"] for f in audit(r)})
    def test_canary_starting_step_oob(self):
        r = rollout()
        r["spec"]["strategy"]["canary"]["analysis"]["startingStep"] = 3
        self.assertIn("AR013", {f["code"] for f in audit(r, template())})
    def test_canary_starting_step_zero(self):
        r = rollout()
        r["spec"]["strategy"]["canary"]["analysis"]["startingStep"] = 0
        self.assertEqual(audit(r, template()), [])
    def test_bluegreen_prepromotion(self):
        r = res("Rollout", {"strategy": {"blueGreen": {
            "prePromotionAnalysis": {"templates": [{"templateName": "gate"}]}}}})
        self.assertEqual(audit(r, template()), [])
    def test_canary_step_inline(self):
        r = res("Rollout", {"strategy": {"canary": {"steps": [{
            "analysis": {"templates": [{"templateName": "gate"}]}}]}}})
        self.assertEqual(audit(r, template()), [])
    def test_non_argo_ignored(self):
        x = template()
        x["apiVersion"] = "example.com/v1"
        self.assertEqual(audit(x), [])
    def test_invalid_yaml_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.yaml"
            p.write_text("kind: [", encoding="utf-8")
            with self.assertRaises(ValueError):
                __import__("audit").load(p)
    def test_empty_doc_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "empty.yaml"
            p.write_text("---\n# blank\n---\nkind: Job\n", encoding="utf-8")
            self.assertEqual(len(__import__("audit").load(p)), 1)
    def test_missing_path_rejected(self):
        with self.assertRaises(ValueError):
            __import__("audit").load("missing-argo-69531.yaml")


if __name__ == "__main__":
    unittest.main()
