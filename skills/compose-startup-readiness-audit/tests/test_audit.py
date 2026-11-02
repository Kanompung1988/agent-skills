import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'audit.py'
spec = importlib.util.spec_from_file_location('compose_audit', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def codes(data):
    return [i['code'] for i in audit.check(data)]

class ComposeTests(unittest.TestCase):
    def test_valid_health_gate(self):
        self.assertEqual(codes({'services': {'db': {'healthcheck': {'test': ['CMD', 'true']}}, 'api': {'depends_on': {'db': {'condition': 'service_healthy'}}}}}), [])
    def test_service_started_warns(self):
        self.assertIn('STARTED_NOT_READY', codes({'services': {'db': {}, 'api': {'depends_on': ['db']}}}))
    def test_missing_service(self):
        self.assertIn('MISSING_SERVICE', codes({'services': {'api': {'depends_on': ['db']}}}))
    def test_cycle(self):
        self.assertIn('DEPENDENCY_CYCLE', codes({'services': {'a': {'depends_on': ['b']}, 'b': {'depends_on': ['a']}}}))
    def test_no_cycle(self):
        self.assertNotIn('DEPENDENCY_CYCLE', codes({'services': {'a': {}, 'b': {'depends_on': ['a']}}}))
    def test_self_cycle(self):
        self.assertIn('DEPENDENCY_CYCLE', codes({'services': {'a': {'depends_on': ['a']}}}))
    def test_unknown_condition(self):
        self.assertIn('UNKNOWN_CONDITION', codes({'services': {'a': {}, 'b': {'depends_on': {'a': {'condition': 'ready'}}}}}))
    def test_healthy_missing_check(self):
        self.assertIn('MISSING_HEALTHCHECK', codes({'services': {'a': {}, 'b': {'depends_on': {'a': {'condition': 'service_healthy'}}}}}))
    def test_healthy_disabled(self):
        self.assertIn('MISSING_HEALTHCHECK', codes({'services': {'a': {'healthcheck': {'test': ['NONE']}}, 'b': {'depends_on': {'a': {'condition': 'service_healthy'}}}}}))
    def test_optional(self):
        self.assertIn('OPTIONAL_DEPENDENCY', codes({'services': {'a': {}, 'b': {'depends_on': {'a': {'required': False}}}}}))
    def test_conflicting_restart(self):
        self.assertIn('CONFLICTING_RESTART', codes({'services': {'a': {'restart': 'always'}, 'b': {'depends_on': {'a': {'condition': 'service_completed_successfully'}}}}}))
    def test_invalid_health_test(self):
        self.assertIn('INVALID_HEALTHCHECK_TEST', codes({'services': {'a': {'healthcheck': {'test': [42]}}}}))
    def test_bad_duration(self):
        self.assertIn('INVALID_HEALTH_DURATION', codes({'services': {'a': {'healthcheck': {'interval': 'abc'}}}}))
    def test_duration_valid(self):
        self.assertNotIn('INVALID_HEALTH_DURATION', codes({'services': {'a': {'healthcheck': {'interval': '1m30s'}}}}))
    def test_retries_bool(self):
        self.assertIn('INVALID_RETRIES', codes({'services': {'a': {'healthcheck': {'retries': True}}}}))
    def test_retries_zero(self):
        self.assertIn('INVALID_RETRIES', codes({'services': {'a': {'healthcheck': {'retries': 0}}}}))
    def test_invalid_root(self):
        self.assertIn('INVALID_SERVICES', codes([]))
    def test_invalid_service(self):
        self.assertIn('INVALID_SERVICE', codes({'services': {'a': []}}))
    def test_bad_depends_on(self):
        self.assertIn('INVALID_DEPENDS_ON', codes({'services': {'a': {'depends_on': 4}}}))
    def test_bad_dep_item(self):
        self.assertIn('INVALID_DEPENDENCY', codes({'services': {'a': {'depends_on': [4]}}}))
    def test_zero_findings(self):
        self.assertEqual(codes({'services': {'db': {}}}), [])
    def test_parse_yaml(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'compose.yml'
            p.write_text('services:\n  db: {}\n', encoding='utf-8')
            self.assertEqual(audit.audit(p), [])
    def test_multi_doc_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'compose.yml'
            p.write_text('services: {}\n---\nservices: {}\n')
            with self.assertRaises(ValueError): audit.audit(p)
    def test_strict_exit(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'compose.yml'
            p.write_text('services:\n  api:\n    depends_on: [missing]\n')
            self.assertEqual(audit.main([str(p), '--strict', '--format', 'json']), 1)
    def test_non_strict_exit(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'compose.yml'
            p.write_text('services:\n  api:\n    depends_on: [missing]\n')
            self.assertEqual(audit.main([str(p)]), 0)
    def test_missing_input_exit(self):
        self.assertEqual(audit.main(['/unlikely/existing/compose.yml']), 2)

if __name__ == '__main__':
    unittest.main()
