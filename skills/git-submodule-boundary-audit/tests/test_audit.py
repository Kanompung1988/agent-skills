import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("audit",ROOT/"scripts"/"audit.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
SHA="a"*40

def command(root,*args):
    proc=subprocess.run(["git","-C",str(root),*args],capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode())
    return proc

def mkrepo(tmp,modules="",gitlink=True):
    root=Path(tmp)
    command(root,"init","-q")
    if modules:
        (root/".gitmodules").write_text(modules)
        command(root,"add",".gitmodules")
    if gitlink:
        command(root,"update-index","--add","--cacheinfo",f"160000,{SHA},vendor/sdk")
    return root

GOOD='[submodule "sdk"]\n path = vendor/sdk\n url = https://example.com/sdk.git\n'

class TestSubmoduleBoundary(unittest.TestCase):
    def test_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit.audit(mkrepo(tmp,GOOD))["count"],0)
    def test_empty_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audit.audit(mkrepo(tmp,gitlink=False))["count"],0)
    def test_http_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=audit.audit(mkrepo(tmp,GOOD.replace("https://","http://")))
            self.assertIn("UNENCRYPTED_TRANSPORT",[x["code"] for x in r["findings"]])
    def test_git_transport(self):
        self.assertEqual(audit.url_issue("git://example.com/repo"),"UNENCRYPTED_TRANSPORT")
    def test_file_url(self): self.assertEqual(audit.url_issue("file:///tmp/repo"),"LOCAL_SOURCE")
    def test_absolute_source(self): self.assertEqual(audit.url_issue("/etc/secrets"),"LOCAL_SOURCE")
    def test_ssh_source(self): self.assertIsNone(audit.url_issue("git@example.com:owner/repo.git"))
    def test_https_source(self): self.assertIsNone(audit.url_issue("https://github.com/a/b"))
    def test_relative_source(self): self.assertIsNone(audit.url_issue("../lib"))
    def test_bad_protocol(self): self.assertEqual(audit.url_issue("ftp://host/repo"),"UNRECOGNIZED_SCHEME")
    def test_no_source(self): self.assertEqual(audit.url_issue(""),"MISSING_URL")
    def test_path_traversal(self): self.assertTrue(audit.unsafe_path("../x"))
    def test_path_dotgit(self): self.assertTrue(audit.unsafe_path("vendor/.git"))
    def test_path_valid(self): self.assertFalse(audit.unsafe_path("vendor/sdk"))
    def test_branch_advisory(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=audit.audit(mkrepo(tmp,GOOD+" branch = main\n"))
            self.assertIn("REMOTE_TRACKING_OPTION",[x["code"] for x in r["findings"]])
    def test_update_rebase(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=audit.audit(mkrepo(tmp,GOOD+" update = rebase\n"))
            self.assertIn("NONCHECKOUT_UPDATE",[x["code"] for x in r["findings"]])
    def test_missing_gitlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=audit.audit(mkrepo(tmp,GOOD,False))
            self.assertIn("MISSING_GITLINK",[x["code"] for x in r["findings"]])
    def test_undeclared_gitlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=audit.audit(mkrepo(tmp))
            self.assertIn("UNDECLARED_GITLINK",[x["code"] for x in r["findings"]])
    def test_unknown_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=audit.audit(mkrepo(tmp,GOOD+" update = !bash\n"))
            self.assertIn("UNKNOWN_UPDATE",[x["code"] for x in r["findings"]])
    def test_duplicate_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            content=GOOD+'[submodule "other"]\n path = vendor/sdk\n url = https://example.com/other.git\n'
            r=audit.audit(mkrepo(tmp,content))
            self.assertIn("DUPLICATE_PATH",[x["code"] for x in r["findings"]])
    def test_invalid_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): audit.audit(tmp)
    def test_bad_path_declared(self):
        with tempfile.TemporaryDirectory() as tmp:
            content=GOOD.replace("vendor/sdk","../escape")
            r=audit.audit(mkrepo(tmp,content))
            self.assertIn("INVALID_PATH",[x["code"] for x in r["findings"]])
    def test_cli_review_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=mkrepo(tmp,GOOD.replace("https://","http://"))
            self.assertEqual(audit.main([str(root),"--json"]),1)
    def test_cli_safe_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=mkrepo(tmp,GOOD)
            self.assertEqual(audit.main([str(root)]),0)

if __name__=="__main__":unittest.main()
