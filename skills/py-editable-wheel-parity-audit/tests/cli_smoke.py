import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from contextlib import redirect_stdout
from io import StringIO
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def make(p,extra=''):
 with ZipFile(p,'w') as z:
  z.writestr('demo-1.dist-info/METADATA','Metadata-Version: 2.3\nName: demo\nVersion: 1.0\n'+extra+'\n')
  z.writestr('demo-1.dist-info/WHEEL','Wheel-Version: 1.0\nTag: py3-none-any\n')
with TemporaryDirectory() as td:
 a=Path(td)/'normal.whl';b=Path(td)/'editable.whl';make(a);make(b)
 with redirect_stdout(StringIO()):assert audit.main([str(a),str(b)])==0
 make(b,'Requires-Dist: editables\n')
 with redirect_stdout(StringIO()):assert audit.main([str(a),str(b),'--strict'])==2
 print('CLI smoke PASS')
