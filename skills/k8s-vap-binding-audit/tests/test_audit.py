import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("audit",Path(__file__).parents[1]/"scripts"/"audit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def policy(name="policy", **extra):
    x={"apiVersion":"admissionregistration.k8s.io/v1",
       "kind":"ValidatingAdmissionPolicy","metadata":{"name":name},
       "spec":{"failurePolicy":"Fail","matchConstraints":{"resourceRules":[{"apiGroups":[""],"apiVersions":["v1"],
                 "operations":["CREATE"],"resources":["pods"]}]},
                "validations":[{"expression":"true"}]}}
    x["spec"].update(extra)
    return x


def binding(policy_name="policy",name="binding",actions=None,**extra):
    x={"apiVersion":"admissionregistration.k8s.io/v1",
       "kind":"ValidatingAdmissionPolicyBinding","metadata":{"name":name},
       "spec":{"policyName":policy_name,
               "validationActions":actions if actions is not None else ["Deny"]}}
    x["spec"].update(extra)
    return x


def rules(*objects):
    return {f["rule"] for f in mod.audit_objects(objects)}


class VAPTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(rules(policy(),binding()),set())

    def test_unused_policy(self):
        self.assertIn("VP012",rules(policy()))

    def test_missing_local_policy(self):
        self.assertIn("VP004",rules(binding("other")))

    def test_missing_name(self):
        self.assertIn("VP003",rules(policy(),binding(policy_name="")))

    def test_action_empty(self):
        self.assertIn("VP005",rules(policy(),binding(actions=[])))

    def test_action_unknown(self):
        self.assertIn("VP005",rules(policy(),binding(actions=["Deny","OTHER"])))

    def test_action_combination(self):
        self.assertIn("VP006",rules(policy(),binding(actions=["Deny","Warn"])))

    def test_warn_only_review(self):
        self.assertIn("VP007",rules(policy(),binding(actions=["Warn","Audit"])))

    def test_audit_only_review(self):
        self.assertIn("VP007",rules(policy(),binding(actions=["Audit"])))

    def test_parameter_missing(self):
        self.assertIn("VP008",rules(policy(paramKind={"apiVersion":"v1","kind":"ConfigMap"}),binding()))

    def test_unnecessary_parameter(self):
        self.assertIn("VP008",rules(policy(),binding(paramRef={"name":"cfg","parameterNotFoundAction":"Deny"})))

    def test_both_selector_and_name(self):
        self.assertIn("VP009",rules(policy(paramKind={"kind":"ConfigMap"}),
             binding(paramRef={"name":"cfg","selector":{"matchLabels":{"a":"b"}},"parameterNotFoundAction":"Deny"})))

    def test_missing_selector_and_name(self):
        self.assertIn("VP009",rules(policy(paramKind={"kind":"ConfigMap"}),
             binding(paramRef={"parameterNotFoundAction":"Deny"})))

    def test_parameter_action_required(self):
        self.assertIn("VP010",rules(policy(paramKind={"kind":"ConfigMap"}),
             binding(paramRef={"name":"cfg"})))

    def test_parameter_action_allow(self):
        self.assertIn("VP011",rules(policy(paramKind={"kind":"ConfigMap"}),
             binding(paramRef={"name":"cfg","parameterNotFoundAction":"Allow"})))

    def test_parameter_action_deny_safe(self):
        self.assertEqual(rules(policy(paramKind={"kind":"ConfigMap"}),
             binding(paramRef={"name":"cfg","parameterNotFoundAction":"Deny"})),set())

    def test_failure_policy_ignore(self):
        self.assertIn("VP013",rules(policy(failurePolicy="Ignore"),binding()))

    def test_missing_resource_rules(self):
        self.assertIn("VP014",rules(policy(matchConstraints={}),binding()))

    def test_duplicate_name(self):
        self.assertIn("VP002",rules(policy(),policy(),binding()))

    def test_wrong_version(self):
        x=policy()
        x["apiVersion"]="admissionregistration.k8s.io/v1beta1"
        self.assertIn("VP001",rules(x))

    def test_ignores_other_objects(self):
        self.assertEqual(rules(policy(),binding(),{"kind":"Deployment"}),set())

    def test_invalid_paramref(self):
        with self.assertRaises(ValueError):
            mod.audit_objects([policy(),binding(paramRef="bad")])

    def test_invalid_metadata(self):
        with self.assertRaises(ValueError):
            mod.audit_objects([{"kind":"ValidatingAdmissionPolicy","apiVersion":
               "admissionregistration.k8s.io/v1","metadata":[],"spec":{}}])

    def test_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.yml"
            p.write_text("apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: ignored\n")
            self.assertEqual(mod.audit_path(tmp)["count"],0)

    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"broken.yml"
            p.write_text("bad: [\n")
            with self.assertRaises(ValueError):
                mod.audit_path(p)


if __name__=="__main__":
    unittest.main()
