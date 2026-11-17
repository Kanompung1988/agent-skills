import importlib.util,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from contextlib import redirect_stdout,redirect_stderr
from io import StringIO
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
BASE='Metadata-Version: 2.3\nName: demo-pkg\nVersion: 1.0\nSummary: demo\nRequires-Dist: requests >=2\n\nDescription\n'
def wheel(path,metadata=BASE,entry='[console_scripts]\ndemo=demo:main\n',wheel=True,extra=None):
    with ZipFile(path,'w') as z:
        if metadata is not None:z.writestr('demo_pkg-1.dist-info/METADATA',metadata)
        if wheel:z.writestr('demo_pkg-1.dist-info/WHEEL','Wheel-Version: 1.0\nTag: py3-none-any\n')
        if entry is not None:z.writestr('demo_pkg-1.dist-info/entry_points.txt',entry)
        for k,v in (extra or {}).items():z.writestr(k,v)
class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.a=Path(self.temp.name)/'a.whl';self.b=Path(self.temp.name)/'b.whl'
        wheel(self.a);wheel(self.b)
    def tearDown(self):self.temp.cleanup()
    def codes(self):return [f['code'] for f in audit.inspect(self.a,self.b)]
    def test_equal(self):self.assertEqual(self.codes(),[])
    def test_normalized_name(self):
        wheel(self.b,BASE.replace('demo-pkg','demo_pkg'));self.assertEqual(self.codes(),[])
    def test_name(self):
        wheel(self.b,BASE.replace('demo-pkg','changed'));self.assertIn('NAME_DRIFT',self.codes())
    def test_version(self):
        wheel(self.b,BASE.replace('Version: 1.0','Version: 2.0'));self.assertIn('VERSION_DRIFT',self.codes())
    def test_summary(self):
        wheel(self.b,BASE.replace('Summary: demo','Summary: other'));self.assertIn('CORE_METADATA_DRIFT',self.codes())
    def test_description(self):
        wheel(self.b,BASE.replace('Description','Other'));self.assertIn('CORE_METADATA_DRIFT',self.codes())
    def test_dependency_removed(self):
        wheel(self.b,BASE.replace('Requires-Dist: requests >=2\n',''));self.assertIn('DROPPED_DEPENDENCY',self.codes())
    def test_added_dependency_requires_review(self):
        wheel(self.b,BASE.replace('Requires-Dist: requests >=2','Requires-Dist: requests >=2\nRequires-Dist: editables'))
        self.assertIn('EDITABLE_ONLY_DEPENDENCY',self.codes())
        self.assertEqual(audit.inspect(self.a,self.b,['editables']),[])
    def test_entry_point(self):
        wheel(self.b,entry=None);self.assertIn('ENTRY_POINTS_DRIFT',self.codes())
    def test_invalid_metadata(self):
        wheel(self.b,metadata=None)
        with self.assertRaises(ValueError):audit.inspect(self.a,self.b)
    def test_invalid_wheel_header(self):
        wheel(self.b,wheel=False)
        with self.assertRaises(ValueError):audit.inspect(self.a,self.b)
    def test_unsafe_members(self):
        wheel(self.b,extra={'../bad':'secret'})
        with self.assertRaises(ValueError):audit.inspect(self.a,self.b)
    def test_corrupt_wheel(self):
        self.b.write_bytes(b'bad')
        with self.assertRaises(ValueError):audit.inspect(self.a,self.b)
    def test_too_large(self):
        wheel(self.b,metadata='A'*2000001)
        with self.assertRaises(ValueError):audit.inspect(self.a,self.b)
    def test_cli_safe(self):
        with redirect_stdout(StringIO()):self.assertEqual(audit.main([str(self.a),str(self.b),'--format','json']),0)
    def test_cli_invalid(self):
        with redirect_stderr(StringIO()):self.assertEqual(audit.main([str(self.a),str(Path(self.temp.name)/'missing')]),1)
if __name__=='__main__':unittest.main()
