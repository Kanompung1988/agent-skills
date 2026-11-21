import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"scripts"))
from audit import audit_documents,audit_file

class JobFailurePolicyTests(unittest.TestCase):
    def codes(self,name): return [x["rule"] for x in audit_file(Path(__file__).parents[1]/"fixtures"/name)]
    def test_safe_fixture(self): self.assertEqual(self.codes("safe.yaml"),[])
    def test_restart_policy_never_required(self): self.assertIn("POD_FAILURE_POLICY_REQUIRES_NEVER",self.codes("review.yaml"))
    def test_replacement_policy_failed_required(self): self.assertIn("POD_REPLACEMENT_POLICY_INCOMPATIBLE",self.codes("review.yaml"))
    def test_per_index_requires_indexed(self): self.assertIn("BACKOFF_PER_INDEX_REQUIRES_INDEXED",self.codes("review.yaml"))
    def test_per_index_requires_never(self): self.assertIn("BACKOFF_PER_INDEX_REQUIRES_NEVER",self.codes("review.yaml"))
    def test_max_failed_requires_per_index(self):
        c=[x["rule"] for x in audit_documents([{"kind":"Job","spec":{"maxFailedIndexes":1}}])]
        self.assertIn("MAX_FAILED_INDEXES_REQUIRES_PER_INDEX",c)
    def test_failindex_requires_per_index(self):
        job={"kind":"Job","spec":{"podFailurePolicy":{"rules":[{"action":"FailIndex","onExitCodes":{"operator":"In","values":[42]}}]},"template":{"spec":{"restartPolicy":"Never"}}}}
        self.assertIn("FAIL_INDEX_REQUIRES_PER_INDEX",[x["rule"] for x in audit_documents([job])])
    def test_unknown_container_detected(self): self.assertIn("EXIT_CODE_CONTAINER_UNKNOWN",self.codes("review.yaml"))
    def test_duplicate_exit_codes_detected(self): self.assertIn("EXIT_CODE_VALUES_ORDER_INVALID",self.codes("review.yaml"))
    def test_exit_code_zero_in_invalid(self): self.assertIn("EXIT_CODE_ZERO_IN_INVALID",self.codes("review.yaml"))
    def test_matcher_mutual_exclusion(self): self.assertIn("POD_FAILURE_RULE_MATCHER_INVALID",self.codes("review.yaml"))
    def test_action_enum(self): self.assertIn("POD_FAILURE_ACTION_INVALID",self.codes("review.yaml"))
    def test_info_indexed_default(self):
        job={"kind":"Job","spec":{"completionMode":"Indexed","backoffLimitPerIndex":1}}
        f=audit_documents([job]); self.assertIn("INDEXED_BACKOFF_DEFAULT",[x["rule"] for x in f])
        self.assertEqual(next(x for x in f if x["rule"]=="INDEXED_BACKOFF_DEFAULT")["severity"],"INFO")
    def test_backoff_limit_nonnegative(self):
        c=[x["rule"] for x in audit_documents([{"kind":"Job","spec":{"backoffLimit":-1}}])]
        self.assertIn("BACKOFF_LIMIT_INVALID",c)
    def test_backoff_per_index_nonnegative(self):
        c=[x["rule"] for x in audit_documents([{"kind":"Job","spec":{"completionMode":"Indexed","backoffLimitPerIndex":-1}}])]
        self.assertIn("BACKOFF_PER_INDEX_INVALID",c)
    def test_max_failed_not_above_completions(self):
        c=[x["rule"] for x in audit_documents([{"kind":"Job","spec":{"completionMode":"Indexed","backoffLimitPerIndex":1,"completions":2,"maxFailedIndexes":3}}])]
        self.assertIn("MAX_FAILED_INDEXES_EXCEEDS_COMPLETIONS",c)
    def test_success_policy_indexed_only(self):
        c=[x["rule"] for x in audit_documents([{"kind":"Job","spec":{"successPolicy":{}}}])]
        self.assertIn("SUCCESS_POLICY_REQUIRES_INDEXED",c)
    def test_cronjob_is_scanned(self):
        cj={"kind":"CronJob","spec":{"jobTemplate":{"spec":{"podFailurePolicy":{"rules":[]},"template":{"spec":{"restartPolicy":"OnFailure"}}}}}}
        c=[x["rule"] for x in audit_documents([cj])]
        self.assertIn("POD_FAILURE_POLICY_REQUIRES_NEVER",c)
        self.assertIn("POD_FAILURE_RULES_REQUIRED",c)
    def test_joblist_is_scanned(self):
        obj={"kind":"JobList","items":[{"kind":"Job","spec":{"podFailurePolicy":{"rules":[]},"template":{"spec":{"restartPolicy":"Never"}}}}]}
        self.assertIn("POD_FAILURE_RULES_REQUIRED",[x["rule"] for x in audit_documents([obj])])
    def test_init_container_name_is_valid(self):
        job={"kind":"Job","metadata":{"name":"x"},"spec":{"template":{"spec":{"restartPolicy":"Never","initContainers":[{"name":"setup"}],"containers":[]}},"podFailurePolicy":{"rules":[{"action":"FailJob","onExitCodes":{"containerName":"setup","operator":"In","values":[42]}}]}}}
        self.assertEqual(audit_documents([job]),[])
    def test_empty_policy_rules(self):
        job={"kind":"Job","spec":{"podFailurePolicy":{"rules":[]},"template":{"spec":{"restartPolicy":"Never"}}}}
        self.assertIn("POD_FAILURE_RULES_REQUIRED",[x["rule"] for x in audit_documents([job])])
    def test_conditions_need_type(self):
        job={"kind":"Job","spec":{"podFailurePolicy":{"rules":[{"action":"Ignore","onPodConditions":[{}]}]},"template":{"spec":{"restartPolicy":"Never"}}}}
        self.assertIn("POD_CONDITIONS_INVALID",[x["rule"] for x in audit_documents([job])])
    def test_exit_values_must_be_nonempty_ints(self):
        job={"kind":"Job","spec":{"podFailurePolicy":{"rules":[{"action":"Ignore","onExitCodes":{"operator":"In","values":[]}}]},"template":{"spec":{"restartPolicy":"Never"}}}}
        self.assertIn("EXIT_CODE_VALUES_INVALID",[x["rule"] for x in audit_documents([job])])
    def test_rule_needs_exactly_one_matcher(self):
        job={"kind":"Job","spec":{"podFailurePolicy":{"rules":[{"action":"Ignore"}]},"template":{"spec":{"restartPolicy":"Never"}}}}
        self.assertIn("POD_FAILURE_RULE_MATCHER_INVALID",[x["rule"] for x in audit_documents([job])])
    def test_parse_error(self):
        p=Path(__file__).parents[1]/"fixtures"/"bad.yaml"; p.write_text("x: [\n",encoding="utf-8")
        try: self.assertIn("INPUT_PARSE_ERROR",[x["rule"] for x in audit_file(p)])
        finally: p.unlink(missing_ok=True)
    def test_unrelated_resource_ignored(self): self.assertEqual(audit_documents([{"kind":"ConfigMap","data":{}}]),[])

if __name__=="__main__": unittest.main()
