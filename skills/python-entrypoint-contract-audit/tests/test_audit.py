import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'audit.py'
spec = importlib.util.spec_from_file_location('entry_audit', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def doc(scripts=None, gui=None, **kw):
    p = {'name': 'demo'}
    if scripts is not None: p['scripts'] = scripts
    if gui is not None: p['gui-scripts'] = gui
    p.update(kw)
    return {'project': p}

def codes(document, root=Path('/tmp/no-package-here'), targets=False):
    return [f['code'] for f in audit.evaluate(document, root, targets)]

class EntryPointTests(unittest.TestCase):
    def test_basic_entrypoint(self): self.assertEqual(codes(doc({'demo': 'foo.cli:main'})), [])
    def test_gui_entrypoint(self): self.assertEqual(codes(doc(gui={'gui': 'foo.app:run'})), [])
    def test_missing_colon(self): self.assertIn('INVALID_REFERENCE', codes(doc({'bad': 'foo.cli'})))
    def test_missing_callable(self): self.assertIn('INVALID_REFERENCE', codes(doc({'bad': 'foo.cli:'})))
    def test_dotted_callable(self): self.assertEqual(codes(doc({'ok': 'foo.cli:App.main'})), [])
    def test_whitespace(self): self.assertEqual(codes(doc({'ok': ' foo.cli : main '})), [])
    def test_extras_review(self): self.assertIn('DEPRECATED_EXTRAS', codes(doc({'x': 'foo.cli:main [cli]'})))
    def test_script_name(self): self.assertIn('INVALID_NAME', codes(doc({'bad script': 'foo.cli:main'})))
    def test_script_name_valid(self): self.assertNotIn('INVALID_NAME', codes(doc({'foo-bar.1': 'foo.cli:main'})))
    def test_private_target(self): self.assertIn('PRIVATE_TARGET', codes(doc({'foo': 'foo.cli:_main'})))
    def test_duplicate(self): self.assertIn('DUPLICATE_COMMAND', codes(doc({'cli': 'foo.cli:main'}, {'cli': 'foo.gui:main'})))
    def test_different_command(self): self.assertNotIn('DUPLICATE_COMMAND', codes(doc({'a': 'foo.cli:main'}, {'b': 'foo.cli:main'})))
    def test_invalid_group(self): self.assertIn('INVALID_GROUP', codes(doc(scripts=['oops'])))
    def test_invalid_object(self): self.assertIn('INVALID_REFERENCE', codes(doc({'x': 7})))
    def test_missing_project(self): self.assertIn('INVALID_PROJECT', codes({}))
    def test_dynamic(self): self.assertIn('DYNAMIC_GROUP', codes(doc(dynamic=['scripts'])))
    def test_conflicting_dynamic(self): self.assertIn('DYNAMIC_STATIC_CONFLICT', codes(doc({'x':'foo.cli:main'}, dynamic=['scripts'])))
    def test_invalid_dynamic(self): self.assertIn('INVALID_DYNAMIC', codes(doc(dynamic='scripts')))
    def test_reserved_group(self): self.assertIn('RESERVED_ENTRY_POINT_GROUP', codes(doc(**{'entry-points': {'console_scripts': {'x': 'foo:bar'}}})))
    def test_bad_nested_group(self): self.assertIn('INVALID_ENTRY_POINTS', codes(doc(**{'entry-points': []})))
    def test_targets_missing(self): self.assertIn('MODULE_NOT_FOUND_LOCALLY', codes(doc({'x': 'foo.cli:main'}), targets=True))
    def test_targets_module_exists(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'src' / 'foo').mkdir(parents=True)
            (root / 'src' / 'foo' / 'cli.py').write_text('def main(): pass\n')
            self.assertNotIn('MODULE_NOT_FOUND_LOCALLY', codes(doc({'x': 'foo.cli:main'}), root, True))
    def test_targets_package_exists(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'foo').mkdir()
            (root / 'foo' / '__init__.py').write_text('')
            self.assertNotIn('MODULE_NOT_FOUND_LOCALLY', codes(doc({'x': 'foo:main'}), root, True))
    def test_parse_toml(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'pyproject.toml').write_text('[project]\nname="ok"\n[project.scripts]\ncli="foo:main"\n')
            self.assertEqual(audit.audit(root/'pyproject.toml', False), [])
    def test_bad_toml(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'pyproject.toml').write_text('[project\n')
            self.assertEqual(audit.main([str(root/'pyproject.toml')]), 2)
    def test_missing_toml(self): self.assertEqual(audit.main(['/unlikely/pyproject.toml']), 2)
    def test_strict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'pyproject.toml').write_text('[project]\nname="x"\n[project.scripts]\nx="invalid"\n')
            self.assertEqual(audit.main([str(root/'pyproject.toml'), '--strict']), 1)
    def test_non_strict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'pyproject.toml').write_text('[project]\nname="x"\n[project.scripts]\nx="invalid"\n')
            self.assertEqual(audit.main([str(root/'pyproject.toml')]), 0)

if __name__ == '__main__': unittest.main()
