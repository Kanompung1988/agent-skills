import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit", ROOT / "scripts" / "audit.py")
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)

def policy(sub="repo:acme/api:ref:refs/heads/main", aud="sts.amazonaws.com"):
    conditions = {"StringEquals": {}}
    if sub is not None:
        conditions["StringEquals"][audit.SUB] = sub
    if aud is not None:
        conditions["StringEquals"][audit.AUD] = aud
    return {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Principal": {"Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"},
        "Action": "sts:AssumeRoleWithWebIdentity", "Condition": conditions}]}

def codes(doc):
    return {item["code"] for item in audit.inspect_policy(doc, "test.json")[0]}

class TrustAuditTests(unittest.TestCase):
    def test_exact_subject_is_clean(self):
        self.assertEqual(codes(policy()), set())
    def test_missing_subject(self):
        self.assertIn("MISSING_POSITIVE_SUB", codes(policy(sub=None)))
    def test_missing_audience(self):
        self.assertIn("MISSING_POSITIVE_AUD", codes(policy(aud=None)))
    def test_wildcard_owner(self):
        self.assertIn("BROAD_REPOSITORY_SUB", codes(policy(sub="repo:*/api:ref:refs/heads/main")))
    def test_wildcard_repo(self):
        self.assertIn("BROAD_REPOSITORY_SUB", codes(policy(sub="repo:acme/*:ref:refs/heads/main")))
    def test_wildcard_branch(self):
        self.assertIn("WILDCARD_REF_SUB", codes(policy(sub="repo:acme/api:ref:refs/heads/*")))
    def test_environment_needs_gate_review(self):
        self.assertIn("ENVIRONMENT_GATES", codes(policy(sub="repo:acme/api:environment:prod")))
    def test_tags_are_exact(self):
        self.assertEqual(codes(policy(sub="repo:acme/api:ref:refs/tags/v1.0.0")), set())
    def test_mixed_subjects_or_broad(self):
        self.assertIn("BROAD_REPOSITORY_SUB", codes(policy(sub=["repo:acme/api:ref:refs/heads/main", "repo:acme/*:ref:refs/heads/main"])))
    def test_nonstandard_audience(self):
        self.assertIn("NONSTANDARD_AUDIENCE", codes(policy(aud="other")))
    def test_multiple_audience(self):
        self.assertIn("MULTIPLE_AUDIENCES", codes(policy(aud=["sts.amazonaws.com", "other"])))
    def test_unsupported_operator(self):
        doc = policy()
        doc["Statement"][0]["Condition"] = {"StringNotLike": {audit.SUB: "repo:other/*"}}
        self.assertIn("UNSUPPORTED_OPERATOR", codes(doc))
        self.assertIn("MISSING_POSITIVE_SUB", codes(doc))
    def test_bare_star_sub(self):
        self.assertIn("BROAD_REPOSITORY_SUB", codes(policy(sub="*")))
    def test_unknown_subject(self):
        self.assertIn("UNRECOGNIZED_SUB", codes(policy(sub="someone@example.com")))
    def test_non_github_provider_ignored(self):
        doc = policy()
        doc["Statement"][0]["Principal"]["Federated"] = "arn:aws:iam::123456789012:oidc-provider/something.invalid"
        self.assertEqual(audit.inspect_policy(doc, "x"), ([], 0))
    def test_deny_ignored(self):
        doc = policy()
        doc["Statement"][0]["Effect"] = "Deny"
        self.assertEqual(audit.inspect_policy(doc, "x"), ([], 0))
    def test_array_statement(self):
        self.assertEqual(audit.inspect_policy(policy(), "x")[1], 1)
    def test_embedded_policy_document(self):
        self.assertEqual(audit.inspect_policy({"AssumeRolePolicyDocument": json.dumps(policy())}, "x")[1], 1)
    def test_invalid_statement_rejected(self):
        with self.assertRaises(audit.InputError):
            audit.inspect_policy({"Statement": "hi"}, "x")
    def test_invalid_condition_flagged(self):
        doc = policy()
        doc["Statement"][0]["Condition"] = "broken"
        self.assertIn("INVALID_CONDITION", codes(doc))
    def test_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "policy.json"
            src.write_text('{"Statement":[],"Statement":[]}', encoding="utf-8")
            with self.assertRaises(audit.InputError):
                audit.audit(src)
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "real.json"
            file.write_text(json.dumps(policy()), encoding="utf-8")
            link = Path(directory) / "link.json"
            try:
                link.symlink_to(file)
            except OSError:
                self.skipTest("symlink unavailable")
            with self.assertRaises(audit.InputError):
                audit.audit(link)
    def test_directory_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "a.json").write_text(json.dumps(policy()), encoding="utf-8")
            (folder / "b.json").write_text(json.dumps(policy(sub=None)), encoding="utf-8")
            output = audit.audit(folder)
            self.assertEqual(output["github_allow_statements"], 2)
            self.assertEqual(output["summary"]["HIGH"], 1)
    def test_cli_exit_codes(self):
        clean = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit.py"),
                                str(ROOT / "examples" / "safe.json"), "--format", "json"],
                               capture_output=True, text=True)
        risky = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit.py"),
                                str(ROOT / "examples" / "review.json"), "--format", "json"],
                               capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertEqual(risky.returncode, 1, risky.stderr)
        self.assertEqual(json.loads(risky.stdout)["findings"][0]["code"], "BROAD_REPOSITORY_SUB")
    def test_no_secret_literal_in_finding(self):
        doc = policy(sub="repo:secretco/*:ref:refs/heads/main")
        self.assertNotIn("secretco", json.dumps(audit.inspect_policy(doc, "x")[0]))
