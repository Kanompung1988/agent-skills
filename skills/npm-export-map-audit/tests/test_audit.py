import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit", ROOT / "scripts" / "audit.py")
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)

def codes(exports, check_files=False):
    return {item["code"] for item in audit.inspect_exports(exports, Path("/tmp"), check_files)[0]}

class ExportsAuditTests(unittest.TestCase):
    def test_simple_valid_target(self):
        self.assertEqual(codes("./dist/index.js"), set())
    def test_root_sugar(self):
        self.assertEqual(codes({".": "./src/index.js"}), set())
    def test_multiple_subpaths(self):
        self.assertEqual(codes({".": "./main.js", "./extra": "./extra.js"}), set())
    def test_conditions(self):
        self.assertEqual(codes({"import": "./mjs.js", "require": "./cjs.cjs"}), set())
    def test_nested_conditions(self):
        self.assertEqual(codes({".": {"import": "./a.js", "default": "./b.js"}}), set())
    def test_null_exports_allowed(self):
        self.assertEqual(codes({"./private/*": None}), set())
    def test_list_fallbacks(self):
        self.assertEqual(codes(["./a.js", "./b.js"]), set())
    def test_empty_list(self):
        self.assertIn("EMPTY_FALLBACK", codes([]))
    def test_external_target(self):
        self.assertIn("INVALID_TARGET_PREFIX", codes("external-module"))
    def test_absolute_target(self):
        self.assertIn("INVALID_TARGET_PREFIX", codes("/tmp/a.js"))
    def test_parent_target(self):
        self.assertIn("INVALID_TARGET_PREFIX", codes("../outside.js"))
    def test_dot_segment(self):
        self.assertIn("INVALID_TARGET_SEGMENT", codes("./a/./b.js"))
    def test_parent_segment(self):
        self.assertIn("INVALID_TARGET_SEGMENT", codes("./a/../b.js"))
    def test_node_modules_segment(self):
        self.assertIn("INVALID_TARGET_SEGMENT", codes("./node_modules/a.js"))
    def test_url_encoded_parent(self):
        self.assertIn("INVALID_TARGET_SEGMENT", codes("./a/%2e%2e/secret.js"))
    def test_url_encoded_node_modules(self):
        self.assertIn("INVALID_TARGET_SEGMENT", codes("./%6eode_modules/x.js"))
    def test_backslash(self):
        self.assertIn("INVALID_TARGET_SEGMENT", codes("./a\\b.js"))
    def test_mixed_map(self):
        self.assertIn("MIXED_EXPORT_KEYS", codes({".": "./index.js", "default": "./other.js"}))
    def test_invalid_key(self):
        self.assertIn("INVALID_EXPORT_KEY", codes({"./lib/../other": "./valid.js"}))
    def test_invalid_value_type(self):
        self.assertIn("INVALID_TARGET_TYPE", codes(True))
    def test_glob_pattern(self):
        self.assertIn("PATTERN_UNRESOLVED", codes({"./features/*": "./src/features/*.js"}))
    def test_missing_built_file_flagged_when_enabled(self):
        self.assertIn("TARGET_NOT_PRESENT", codes("./almost-certainly-missing-df39a8.js", True))
    def test_missing_built_file_ignored_by_default(self):
        self.assertNotIn("TARGET_NOT_PRESENT", codes("./almost-certainly-missing-df39a8.js"))
    def test_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "main.js").write_text("export default 1")
            findings, _ = audit.inspect_exports("./main.js", path, check_files=True)
            self.assertEqual(findings, [])
    def test_symlink_escape_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "escape.js").symlink_to(Path("/tmp/outside-file.js"))
            self.assertIn("INVALID_TARGET_SEGMENT", {x["code"] for x in audit.inspect_exports("./escape.js", root)[0]})
    def test_duplicate_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.json"
            path.write_text('{"exports":{".":"./a.js",".":"./b.js"}}')
            with self.assertRaises(audit.InputError):
                audit.audit(path)
    def test_no_exports_explicitly_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.json"
            path.write_text('{"name":"x"}')
            self.assertFalse(audit.audit(path)["exports_present"])
    def test_malformed_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "package.json"
            path.write_text("{invalid")
            with self.assertRaises(audit.InputError):
                audit.audit(path)
    def test_cli_safe_and_review(self):
        safe = subprocess.run([sys.executable, str(ROOT/"scripts"/"audit.py"), str(ROOT/"examples"/"safe"), "--format", "json"], capture_output=True, text=True)
        risky = subprocess.run([sys.executable, str(ROOT/"scripts"/"audit.py"), str(ROOT/"examples"/"review"), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(safe.returncode, 0, safe.stderr)
        self.assertEqual(risky.returncode, 1, risky.stderr)
        self.assertIn("INVALID_TARGET_PREFIX", {x["code"] for x in json.loads(risky.stdout)["findings"]})
    def test_cli_invalid_input_exit_two(self):
        result = subprocess.run([sys.executable, str(ROOT/"scripts"/"audit.py"), str(ROOT/"examples"/"does-not-exist")], capture_output=True)
        self.assertEqual(result.returncode, 2)
