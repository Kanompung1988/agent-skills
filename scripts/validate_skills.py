"""Discover and validate all portable Agent Skills; optionally run their tests.

This is an offline repository policy validator, not the official skills-ref package.
Use `skills-ref validate` separately when the reference tool is available.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def discover_skills(base: Path = SKILLS) -> list[Path]:
    if not base.is_dir():
        raise ValueError(f"Missing skills directory: {base}")
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))


def check_skill(folder: Path) -> list[str]:
    errors: list[str] = []
    doc = folder / "SKILL.md"
    if not doc.is_file():
        return [f"{folder.name}: SKILL.md missing"]
    try:
        text = doc.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"{folder.name}: unreadable SKILL.md: {exc}"]
    match = FRONTMATTER.match(text)
    if not match:
        return [f"{folder.name}: YAML frontmatter is missing or not enclosed by ---"]
    values: dict[str, str] = {}
    for raw in match.group("body").splitlines():
        if not raw.strip() or raw.startswith((" ", "\t")):
            continue
        if ":" not in raw:
            errors.append(f"{folder.name}: malformed frontmatter line: {raw[:80]}")
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        if key in values:
            errors.append(f"{folder.name}: duplicate frontmatter field: {key}")
        values[key] = value.strip().strip('"\'')
        if key not in ALLOWED:
            errors.append(f"{folder.name}: unsupported frontmatter field: {key}")
    name = values.get("name", "")
    if len(name) > 64 or not NAME.fullmatch(name) or name != folder.name:
        errors.append(f"{folder.name}: name must match folder, lowercase kebab-case, <=64 chars")
    description = values.get("description", "")
    # A compact one-line description is this repository's convention, not a spec limitation.
    if not description or len(description) > 1024 or description in (">", "|", ">-", "|-"):
        errors.append(f"{folder.name}: provide a nonempty single-line description <=1024 chars")
    if "Use when" not in text:
        errors.append(f"{folder.name}: missing explicit 'Use when' trigger section")
    if "Workflow" not in text:
        errors.append(f"{folder.name}: missing Workflow section")
    if "Edge cases" not in text:
        errors.append(f"{folder.name}: missing Edge cases section")
    if len(text.splitlines()) >= 500:
        errors.append(f"{folder.name}: SKILL.md should stay below 500 lines")
    for required in ("README.md", "LICENSE"):
        if not (folder / required).is_file():
            errors.append(f"{folder.name}: required {required} missing")
    scripts = folder / "scripts"
    if not scripts.is_dir() or not any(scripts.glob("*.py")):
        errors.append(f"{folder.name}: expected at least one Python CLI in scripts/")
    tests = folder / "tests"
    if not tests.is_dir() or not any(tests.glob("test_*.py")):
        errors.append(f"{folder.name}: tests/test_*.py required for CI discovery")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true", help="Check every skill package")
    actions.add_argument("--run-tests", action="store_true", help="Run unittest in every skill's tests directory")
    options = parser.parse_args(argv)
    skills = discover_skills()
    if not skills:
        print("ERROR: no skills found", file=sys.stderr)
        return 1
    issues = [problem for folder in skills for problem in check_skill(folder)]
    if issues:
        print("\n".join(f"ERROR: {problem}" for problem in issues), file=sys.stderr)
        return 1
    print(f"Validated {len(skills)} portable Agent Skill package(s): {', '.join(s.name for s in skills)}", flush=True)
    if options.run_tests:
        for skill in skills:
            print(f"\n>>> Running {skill.name} tests", flush=True)
            proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(skill / "tests"), "-v"], cwd=ROOT, check=False, timeout=180)
            if proc.returncode:
                print(f"ERROR: tests failed for {skill.name}", file=sys.stderr)
                return proc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())