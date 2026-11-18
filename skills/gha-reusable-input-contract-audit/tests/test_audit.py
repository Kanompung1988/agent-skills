import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1]/'scripts/audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

CALLEE = """on:\n  workflow_call:\n    inputs:\n      env:\n        required: true\n        type: string\n      retry:\n        type: number\n      ready:\n        type: boolean\n    secrets:\n      TOKEN:\n        required: true\njobs: {}\n"""

def caller(with_text='    with:\n      env: production\n',secrets='    secrets:\n      TOKEN: ${{ secrets.TOKEN }}\n',use='./.github/workflows/callee.yml'):
    return f'jobs:\n  deploy:\n    uses: {use}\n{with_text}{secrets}'

class TestAudit(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p=Path(self.temp.name)
        (self.p/'callee.yml').write_text(CALLEE)
    def check(self,workflow=None):
        (self.p/'caller.yaml').write_text(workflow if workflow is not None else caller())
        return audit.findings(self.p)
    def codes(self,workflow=None):return {x['code'] for x in self.check(workflow)}
    def test_valid(self):self.assertEqual([],self.check())
    def test_missing_input(self):self.assertIn('MISSING_INPUT',self.codes(caller(with_text='')))
    def test_missing_secret(self):self.assertIn('MISSING_SECRET',self.codes(caller(secrets='')))
    def test_unknown_input(self):self.assertIn('UNKNOWN_INPUT',self.codes(caller(with_text='    with:\n      env: prod\n      bogus: x\n')))
    def test_unknown_secret_review(self):
        hits=self.check(caller(secrets='    secrets:\n      TOKEN: ok\n      EXTRA: test\n'))
        self.assertEqual('review',next(x['severity'] for x in hits if x['code']=='UNKNOWN_SECRET'))
    def test_number_mismatch(self):self.assertIn('INPUT_TYPE',self.codes(caller(with_text='    with:\n      env: prod\n      retry: nope\n')))
    def test_number_valid(self):self.assertEqual([],self.check(caller(with_text='    with:\n      env: prod\n      retry: 2.5\n')))
    def test_boolean_mismatch(self):self.assertIn('INPUT_TYPE',self.codes(caller(with_text='    with:\n      env: prod\n      ready: yes\n')))
    def test_boolean_valid(self):self.assertEqual([],self.check(caller(with_text='    with:\n      env: prod\n      ready: false\n')))
    def test_dynamic_expression(self):self.assertEqual([],self.check(caller(with_text='    with:\n      env: prod\n      retry: ${{ inputs.retry }}\n')))
    def test_inherited_secret(self):self.assertEqual([],self.check(caller(secrets='    secrets: inherit\n')))
    def test_missing_callee_review(self):self.assertIn('MISSING_CALLEE',self.codes(caller(use='./.github/workflows/unknown.yml')))
    def test_path_traversal(self):self.assertIn('UNSAFE_CALLEE_PATH',self.codes(caller(use='./.github/workflows/../outside.yml')))
    def test_not_reusable(self):
        (self.p/'callee.yml').write_text('on: push\njobs: {}\n')
        self.assertIn('NOT_REUSABLE',self.codes())
    def test_default_satisfies_input(self):
        (self.p/'callee.yml').write_text(CALLEE.replace('required: true\n        type: string','required: true\n        default: dev\n        type: string'))
        self.assertNotIn('MISSING_INPUT',self.codes(caller(with_text='')))
    def test_on_key_retained(self):self.assertIn('workflow_call',audit.load(self.p/'callee.yml')['on'])
    def test_invalid_yaml(self):
        (self.p/'broken.yml').write_text('jobs: [unterminated')
        self.assertIn('INVALID_YAML',self.codes())
    def test_size_limit(self):
        (self.p/'huge.yml').write_text('a'*1_000_001)
        self.assertIn('INVALID_YAML',self.codes())
    def test_missing_dir(self):
        with self.assertRaises(ValueError):audit.findings(self.p/'none')
    def test_output_exit_codes(self):
        self.assertEqual(0,audit.main([str(self.p),'--json']))
        (self.p/'caller.yaml').write_text(caller(with_text=''))
        self.assertEqual(2,audit.main([str(self.p),'--json']))
        self.assertEqual(0,audit.main([str(self.p),'--fail-on','never']))

if __name__=='__main__':unittest.main()
