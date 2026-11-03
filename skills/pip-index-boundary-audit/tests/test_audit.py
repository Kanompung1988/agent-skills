import tempfile
from pathlib import Path
import unittest
from audit import audit, _tokens

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def put(self, text, path='requirements.txt'):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p
    def codes(self, text):
        p = self.put(text)
        return [d['code'] for d in audit(self.root, p)]
    def test_safe(self):
        self.assertEqual(self.codes('requests==2.0\n'), [])
    def test_extra_index(self):
        self.assertIn('EXTRA_INDEX', self.codes('--extra-index-url https://internal.invalid/simple\n'))
    def test_extra_equals(self):
        self.assertIn('EXTRA_INDEX', self.codes('--extra-index-url=https://internal.invalid/simple\n'))
    def test_multiple(self):
        self.assertIn('MULTI_INDEX', self.codes('--index-url https://pypi.org/simple\n--extra-index-url https://private.invalid/simple\n'))
    def test_http(self):
        self.assertIn('PLAIN_HTTP_INDEX', self.codes('--index-url http://mirror.invalid/simple'))
    def test_trusted(self):
        self.assertIn('TRUSTED_HOST', self.codes('--trusted-host mirror.invalid'))
    def test_nested(self):
        self.put('--extra-index-url https://internal.invalid/simple\n', 'nested.txt')
        self.assertIn('EXTRA_INDEX', self.codes('-r nested.txt'))
    def test_constraint(self):
        self.put('--trusted-host mirror.invalid', 'constraints/base.txt')
        self.assertIn('TRUSTED_HOST', self.codes('-c constraints/base.txt'))
    def test_cycle(self):
        self.put('-r requirements.txt', 'nested.txt')
        self.assertEqual(self.codes('-r nested.txt'), [])
    def test_outside(self):
        self.assertIn('OUTSIDE_ROOT', self.codes('-r ../missing.txt'))
    def test_quotes(self):
        self.assertEqual(_tokens("'unterminated"), None)
    def test_invalid_quotes(self):
        self.assertIn('INVALID_SHELL_QUOTING', self.codes("'unterminated"))
    def test_unknown_scheme(self):
        self.assertIn('UNKNOWN_INDEX_SCHEME', self.codes('--index-url ftp://mirror.invalid/simple'))
    def test_no_echo_credentials(self):
        p = self.put('--extra-index-url https://user:secret@mirror.invalid/simple')
        self.assertNotIn('secret', repr(audit(self.root, p)))
    def test_ignored_comments(self):
        self.assertEqual(self.codes('# --trusted-host mirror.invalid\n'), [])
    def test_missing_include(self):
        self.assertIn('INVALID_INCLUDE', self.codes('-r'))
    def test_root_directory(self):
        self.assertIn('OUTSIDE_ROOT', [f['code'] for f in audit(self.root / 'other', self.put('ok'))])
    def test_bounded_read(self):
        self.put('x' * 1_000_001)
        self.assertIn('UNREADABLE', [f['code'] for f in audit(self.root, self.root / 'requirements.txt')])
    def test_index_equals_http(self):
        self.assertIn('PLAIN_HTTP_INDEX', self.codes('--extra-index-url=http://mirror.invalid'))
    def test_hyphen_raises_no_crash(self):
        self.assertIn('INVALID_INCLUDE', self.codes('--requirement'))

if __name__ == '__main__':
    unittest.main()
