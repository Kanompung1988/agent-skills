import unittest
from audit import audit, labels_match

def budget(selector, **kw):
    return {'kind': 'PodDisruptionBudget', 'apiVersion': 'policy/v1',
            'metadata': {'name': 'web', 'namespace': 'prod'},
            'spec': {'selector': selector, 'minAvailable': 1, **kw}}

def pod(labels, name='a', namespace='prod'):
    return {'kind': 'Pod', 'metadata': {'name': name, 'namespace': namespace, 'labels': labels}}

class Tests(unittest.TestCase):
    def codes(self, docs):
        return [x['code'] for x in audit(docs)]
    def test_match_labels(self):
        self.assertTrue(labels_match({'matchLabels': {'app': 'a'}}, {'app': 'a'}))
    def test_mismatch(self):
        self.assertFalse(labels_match({'matchLabels': {'app': 'a'}}, {'app': 'b'}))
    def test_in(self):
        self.assertTrue(labels_match({'matchExpressions': [{'key': 'tier', 'operator': 'In', 'values': ['api']}]}, {'tier': 'api'}))
    def test_notin_requires_key(self):
        self.assertFalse(labels_match({'matchExpressions': [{'key': 'a', 'operator': 'NotIn', 'values': ['x']}]}, {}))
    def test_notin_match(self):
        self.assertTrue(labels_match({'matchExpressions': [{'key': 'a', 'operator': 'NotIn', 'values': ['x']}]}, {'a': 'y'}))
    def test_exists(self):
        self.assertTrue(labels_match({'matchExpressions': [{'key': 'a', 'operator': 'Exists'}]}, {'a': ''}))
    def test_does_not_exist(self):
        self.assertTrue(labels_match({'matchExpressions': [{'key': 'a', 'operator': 'DoesNotExist'}]}, {}))
    def test_unknown_operator(self):
        self.assertIsNone(labels_match({'matchExpressions': [{'key': 'a', 'operator': 'Maybe'}]}, {}))
    def test_empty_selector_matches_all(self):
        self.assertIn('ALL_PODS', self.codes([budget({})]))
    def test_null_selector(self):
        self.assertIn('NULL_SELECTOR', self.codes([budget(None)]))
    def test_budget_missing(self):
        d = budget({'matchLabels': {'app': 'web'}})
        d['spec'].pop('minAvailable')
        self.assertIn('BUDGET_FIELDS', self.codes([d]))
    def test_budget_mutual_exclusive(self):
        self.assertIn('BUDGET_FIELDS', self.codes([budget({}, maxUnavailable=1)]))
    def test_invalid_percentage(self):
        self.assertIn('INVALID_BUDGET', self.codes([budget({}, minAvailable='101%')]))
    def test_zero_evictions(self):
        self.assertIn('ZERO_DISRUPTIONS', self.codes([budget({}, minAvailable='100%')]))
    def test_overlap(self):
        a = budget({'matchLabels': {'app': 'x'}})
        b = budget({'matchLabels': {'tier': 'api'}})
        b['metadata']['name'] = 'overlap'
        self.assertIn('OVERLAP', self.codes([pod({'app': 'x', 'tier': 'api'}), a, b]))
    def test_separate_namespaces(self):
        self.assertIn('NO_PODS_IN_INPUT', self.codes([pod({'app':'x'}, namespace='staging'), budget({'matchLabels': {'app':'x'}})]))
    def test_unrecognized_docs(self):
        self.assertIn('NO_BUDGETS', self.codes([{'kind': 'ConfigMap'}]))
    def test_unsupported_selector(self):
        self.assertIn('UNSUPPORTED_SELECTOR', self.codes([pod({'a': 'b'}), budget({'unexpected': True})]))
    def test_clean_matching(self):
        self.assertEqual([], audit([pod({'app': 'web'}), budget({'matchLabels': {'app': 'web'}})]))
    def test_invalid_document(self):
        self.assertIn('INVALID_DOCUMENT', self.codes(['hello']))

if __name__ == '__main__':
    unittest.main()
