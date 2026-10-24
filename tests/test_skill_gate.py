"""Regression tests for dynamic Agent Skills discovery, validation and CI policy."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "validate_skills.py"
spec = importlib.util.spec_from_file_location("areazero_validate_skills", MODULE)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def fixture(folder: Path, name: str = "sample-skill", description: str = "Use when reviewing sample scripts.") -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n\n## Use when\nSample\n## Workflow\nSample\n## Edge cases\nSample\n", encoding="utf-8")
    (folder / "README.md").write_text("# Example\n", encoding="utf-8")
    (folder / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (folder / "scripts").mkdir(exist_ok=True)
    (folder / "scripts" / "sample.py").write_text("print('example')\n", encoding="utf-8")
    (folder / "tests").mkdir(exist_ok=True)
    (folder / "tests" / "test_sample.py").write_text("import unittest\nclass TestSample(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n", encoding="utf-8")


class SkillGateTests(unittest.TestCase):
    def test_discovers_current_portable_skills(self):
        names = [p.name for p in validator.discover_skills(ROOT / "skills")]
        self.assertIn("openapi-compat-audit", names)
        self.assertIn("ci-log-triage", names)

    def test_valid_fixture(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / "sample-skill"
            fixture(folder)
            self.assertEqual(validator.check_skill(folder), [])

    def test_rejects_wrong_frontmatter_name(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / "sample-skill"
            fixture(folder, name="wrong-name")
            self.assertTrue(any("name must match" in item for item in validator.check_skill(folder)))

    def test_rejects_missing_test_suite(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / "sample-skill"
            fixture(folder)
            (folder / "tests" / "test_sample.py").unlink()
            self.assertTrue(any("tests/test_" in item for item in validator.check_skill(folder)))

    def test_rejects_missing_readme(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / "sample-skill"
            fixture(folder)
            (folder / "README.md").unlink()
            self.assertTrue(any("README.md missing" in item for item in validator.check_skill(folder)))

    def test_rejects_missing_description(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / "sample-skill"
            fixture(folder, description="")
            self.assertTrue(any("description" in item for item in validator.check_skill(folder)))

    def test_rejects_consecutive_hyphens(self):
        with tempfile.TemporaryDirectory() as base:
            folder = Path(base) / "sample--skill"
            fixture(folder, name="sample--skill")
            self.assertTrue(any("name must match" in item for item in validator.check_skill(folder)))


if __name__ == "__main__":
    unittest.main()