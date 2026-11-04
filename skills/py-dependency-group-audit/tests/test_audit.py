import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / 'scripts' / 'audit.py'
spec = importlib.util.spec_from_file_location('auditor', FILE)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class DependencyGroupsTests(unittest.TestCase):
    def codes(self, groups):
        return [x['code'] for x in a.audit({'dependency-groups': groups})]

    def test_empty(self): self.assertEqual(self.codes({}), [])
    def test_basic(self): self.assertEqual(self.codes({'test': ['pytest>=7']}), [])
    def test_valid_url(self): self.assertEqual(self.codes({'test': ['pkg @ https://example.com/pkg.whl']}), [])
    def test_valid_markers(self): self.assertEqual(self.codes({'test': ['pytest; python_version >= "3.10"']}), [])
    def test_valid_extras(self): self.assertEqual(self.codes({'test': ['package[one,two]>=1']}), [])
    def test_valid_include(self): self.assertEqual(self.codes({'lint': ['ruff'], 'all': [{'include-group': 'lint'}]}), [])
    def test_case_fold_include(self): self.assertEqual(self.codes({'My_test': ['ruff'], 'all': [{'include-group': 'my-test'}]}), [])
    def test_name_collision(self): self.assertIn('NAME_COLLISION', self.codes({'My_test': [], 'my.test': []}))
    def test_not_table(self): self.assertIn('GROUPS_NOT_TABLE', [x['code'] for x in a.audit({'dependency-groups': []})])
    def test_not_list(self): self.assertIn('GROUP_NOT_LIST', self.codes({'test': 'pytest'}))
    def test_invalid_requirement(self): self.assertIn('INVALID_REQUIREMENT', self.codes({'test': ['-r requirements.txt']}))
    def test_local_path(self): self.assertIn('INVALID_REQUIREMENT', self.codes({'test': ['./mypkg']}))
    def test_bad_dict(self): self.assertIn('INVALID_INCLUDE', self.codes({'a': [{'unknown': 'b'}]}))
    def test_dict_extra_key(self): self.assertIn('INVALID_INCLUDE', self.codes({'a': [{'include-group': 'b', 'foo': 2}]}))
    def test_non_string_target(self): self.assertIn('INVALID_INCLUDE', self.codes({'a': [{'include-group': 123}]}))
    def test_missing_target(self): self.assertIn('UNKNOWN_GROUP', self.codes({'a': [{'include-group': 'absent'}]}))
    def test_entry_number(self): self.assertIn('INVALID_ENTRY', self.codes({'a': [3]}))
    def test_entry_boolean(self): self.assertIn('INVALID_ENTRY', self.codes({'a': [True]}))
    def test_self_cycle(self): self.assertIn('INCLUDE_CYCLE', self.codes({'a': [{'include-group': 'a'}]}))
    def test_mutual_cycle(self): self.assertIn('INCLUDE_CYCLE', self.codes({'a': [{'include-group':'b'}], 'b':[{'include-group':'a'}]}))
    def test_no_cycle_diamond(self): self.assertEqual(self.codes({'a':['ruff'],'b':[{'include-group':'a'}],'c':[{'include-group':'a'}],'d':[{'include-group':'b'},{'include-group':'c'}]}), [])
    def test_skip_empty(self): self.assertEqual(self.codes({'a':['']}), ['INVALID_REQUIREMENT'])
    def test_main_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'pyproject.toml';p.write_text('[dependency-groups]\ntest = ["-r req.txt"]\n')
            out=io.StringIO()
            with redirect_stdout(out): code=a.main([str(p),'--json'])
            self.assertEqual(code,1)
            self.assertEqual(json.loads(out.getvalue())['count'],1)
    def test_main_ok(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'pyproject.toml';p.write_text('[dependency-groups]\ntest = ["pytest"]\n')
            with redirect_stdout(io.StringIO()): code=a.main([str(p)])
            self.assertEqual(code,0)
    def test_main_bad_toml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'pyproject.toml';p.write_text('broken= [')
            self.assertEqual(a.main([str(p)]),2)

if __name__ == '__main__': unittest.main()
