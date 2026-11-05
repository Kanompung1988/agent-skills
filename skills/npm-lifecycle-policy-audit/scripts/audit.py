#!/usr/bin/env python3
"""Offline, read-only npm lifecycle script policy checker (stdlib only)."""
import argparse
import json
import sys
from pathlib import Path

MAX_BYTES = 2_000_000
INSTALL = ("preinstall", "install", "postinstall", "prepublish",
           "preprepare", "prepare", "postprepare")
PACK = ("prepack", "postpack", "prepublishOnly", "publish", "postpublish")
MUTATION = ("dependencies",)
LIFECYCLE = set(INSTALL + PACK + MUTATION)


def audit_object(package, binding_gyp=False, allowed=()):
    """Return stable findings without returning script commands or secret values."""
    if not isinstance(package, dict):
        raise ValueError("package.json top-level must be an object")
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        raise ValueError("package.json scripts must be an object")
    allowed = set(allowed)
    findings = []

    def note(rule, event, description):
        findings.append({"rule": rule, "event": event, "message": description})

    for event in sorted(scripts):
        value = scripts[event]
        if not isinstance(event, str) or not isinstance(value, str):
            note("NPM005", "<invalid>", "scripts keys and commands must be strings")
            continue
        if event in allowed:
            continue
        if event == "prepublish":
            note("NPM006", event, "Deprecated hook can run on npm ci/install, not just publishing")
        elif event in INSTALL:
            note("NPM001", event, "Lifecycle hook can run during install/ci for this package")
        elif event in PACK:
            note("NPM002", event, "Lifecycle hook can run during pack or publishing")
        elif event in MUTATION:
            note("NPM003", event, "Lifecycle hook runs after node_modules mutations")
    if binding_gyp and "install" not in scripts and "preinstall" not in scripts and "install" not in allowed:
        note("NPM004", "install", "binding.gyp without install/preinstall may trigger default node-gyp rebuild")
    findings.sort(key=lambda f: (f["rule"], f["event"]))
    return findings


def audit_file(path, allowed=()):
    """Parse only the provided JSON file; avoid symlink traversal, network and code execution."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Input must be a regular non-symlink package.json file")
    if path.name != "package.json":
        raise ValueError("Expected a file named package.json")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("package.json exceeds 2MB safety cap")
    package = json.loads(path.read_text(encoding="utf-8"))
    gyp = path.parent / "binding.gyp"
    # No read of binding.gyp contents is needed.
    return audit_object(package, binding_gyp=gyp.is_file() and not gyp.is_symlink(), allowed=allowed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to package.json (or its containing directory)")
    parser.add_argument("--allow", action="append", default=[], help="Explicitly reviewed lifecycle hook name (repeatable)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not all(a in LIFECYCLE for a in args.allow):
        print("INPUT ERROR: --allow must name a known lifecycle hook", file=sys.stderr)
        return 2
    path = args.path / "package.json" if args.path.is_dir() else args.path
    try:
        findings = audit_file(path, allowed=args.allow)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        print(f"{len(findings)} finding(s)")
        for f in findings:
            print(f"{f['rule']} [{f['event']}]: {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
