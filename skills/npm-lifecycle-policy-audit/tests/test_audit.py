import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit import audit_object, audit_file, main


def rules(data, gyp=False, allowed=()):
    return [x["rule"] for x in audit_object(data, gyp, allowed)]

class LifecycleTests(unittest.TestCase):
    def test_empty(self): self.assertEqual([], rules({}))
    def test_normal_script(self): self.assertEqual([], rules({"scripts":{"test":"jest","build":"tsc"}}))
    def test_postinstall(self): self.assertEqual(["NPM001"], rules({"scripts":{"postinstall":"node setup.js"}}))
    def test_prepare(self): self.assertEqual(["NPM001"], rules({"scripts":{"prepare":"npm run build"}}))
    def test_preprepare(self): self.assertEqual(["NPM001"], rules({"scripts":{"preprepare":"true"}}))
    def test_postprepare(self): self.assertEqual(["NPM001"], rules({"scripts":{"postprepare":"true"}}))
    def test_prepublish(self): self.assertEqual(["NPM006"], rules({"scripts":{"prepublish":"echo hey"}}))
    def test_prepack(self): self.assertEqual(["NPM002"], rules({"scripts":{"prepack":"echo hey"}}))
    def test_postpack(self): self.assertEqual(["NPM002"], rules({"scripts":{"postpack":"echo hey"}}))
    def test_prepubonly(self): self.assertEqual(["NPM002"], rules({"scripts":{"prepublishOnly":"echo hey"}}))
    def test_publish(self): self.assertEqual(["NPM002"], rules({"scripts":{"publish":"echo hey"}}))
    def test_dependencies(self): self.assertEqual(["NPM003"], rules({"scripts":{"dependencies":"echo hey"}}))
    def test_implicit_gyp(self): self.assertEqual(["NPM004"], rules({}, True))
    def test_explicit_install_overrides_gyp(self): self.assertEqual(["NPM001"], rules({"scripts":{"install":"node build.js"}}, True))
    def test_allow(self): self.assertEqual([], rules({"scripts":{"prepare":"echo fine"}}, allowed=("prepare",)))
    def test_multiple(self):
        self.assertEqual(["NPM001","NPM002"], rules({"scripts":{"prepare":"x","prepack":"y"}}))
    def test_bad_scripts(self):
        with self.assertRaises(ValueError): audit_object({"scripts":[]})
    def test_bad_top(self):
        with self.assertRaises(ValueError): audit_object([])
    def test_bad_command(self): self.assertEqual(["NPM005"], rules({"scripts":{"prepare": 123}}))
    def test_json_does_not_echo_commands(self):
        result=audit_object({"scripts":{"preinstall":"TOKEN=TOPSECRET curl example.com"}})
        self.assertNotIn("TOPSECRET", str(result))
    def test_dir_input(self):
        safe=Path(__file__).resolve().parents[1]/"examples/safe"
        self.assertEqual(0,main([str(safe)]))
    def test_review_json(self):
        risky=Path(__file__).resolve().parents[1]/"examples/review"
        self.assertEqual(1,main([str(risky), "--json"]))
    def test_bad_allow(self):
        safe=Path(__file__).resolve().parents[1]/"examples/safe"
        self.assertEqual(2,main([str(safe), "--allow","foobar"]))
    def test_missing_file(self):
        self.assertEqual(2,main(["/does/not/exist/package.json"]))
    def test_implicit_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"package.json"
            path.write_text('{"name":"demo","scripts":{}}', encoding="utf-8")
            (Path(d)/"binding.gyp").write_text("{}",encoding="utf-8")
            self.assertEqual(["NPM004"], [x["rule"] for x in audit_file(path)])
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"original.json"; source.write_text("{}",encoding="utf-8")
            target=Path(d)/"package.json";target.symlink_to(source)
            with self.assertRaises(ValueError): audit_file(target)
    def test_large_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"package.json";target.write_text(" "*(2_000_001),encoding="utf-8")
            with self.assertRaises(ValueError): audit_file(target)
if __name__=="__main__": unittest.main()
