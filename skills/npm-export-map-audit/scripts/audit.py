#!/usr/bin/env python3
"""Offline check of Node.js package.json exports targets and path safety."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import unquote

MAX_BYTES = 2_000_000

class InputError(Exception):
    pass

def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result

def _finding(code, severity, location, detail):
    return {"code": code, "severity": severity, "location": location, "detail": detail}

def _invalid_segment(text):
    tail = text[2:] if text.startswith("./") else text
    lower = unquote(tail).lower()
    encoded = tail.lower()
    segments = lower.split("/")
    return (
        "\\" in lower
        or any(segment in (".", "..", "node_modules", "") for segment in segments)
        or "%2f" in encoded or "%5c" in encoded or "\x00" in lower
    )

def _safe_under_root(root, value):
    try:
        target = (root / value[2:]).resolve()
        base = root.resolve()
        return target == base or base in target.parents
    except (OSError, RuntimeError):
        return False

def inspect_exports(exports, root, check_files=False):
    findings = []
    target_count = 0
    def flag(code, level, path, detail):
        findings.append(_finding(code, level, path, detail))

    def walk(value, pointer, key=None):
        nonlocal target_count
        if value is None:
            return
        if isinstance(value, str):
            target_count += 1
            if not value.startswith("./"):
                flag("INVALID_TARGET_PREFIX", "HIGH", pointer,
                     "Export target must be a relative package path beginning ./")
                return
            if _invalid_segment(value) or not _safe_under_root(root, value.replace("*", "placeholder")):
                flag("INVALID_TARGET_SEGMENT", "HIGH", pointer,
                     "Export target contains disallowed path segment or escapes package root.")
                return
            if "*" in value or key is not None and "*" in key:
                flag("PATTERN_UNRESOLVED", "REVIEW", pointer,
                     "Subpath pattern requires Node-aware expansion and package-file inventory.")
                return
            if check_files:
                target = root / value[2:]
                if target.is_symlink() or not target.is_file():
                    flag("TARGET_NOT_PRESENT", "REVIEW", pointer,
                         "Export target is not a regular file in this working tree; it may be generated at build time.")
            return
        if isinstance(value, list):
            if not value:
                flag("EMPTY_FALLBACK", "REVIEW", pointer,
                     "Empty target fallbacks cannot resolve a public export.")
            for index, entry in enumerate(value):
                walk(entry, pointer + "/" + str(index), key=key)
            return
        if isinstance(value, dict):
            keys = list(value)
            subpaths = [k for k in keys if isinstance(k, str) and k.startswith(".")]
            conditions = [k for k in keys if isinstance(k, str) and not k.startswith(".")]
            if subpaths and conditions:
                flag("MIXED_EXPORT_KEYS", "HIGH", pointer,
                     "Subpath export keys and condition keys are mixed at one object level.")
            for name, entry in value.items():
                if not isinstance(name, str):
                    flag("INVALID_EXPORT_KEY", "HIGH", pointer,
                         "Export mapping keys must be strings.")
                    continue
                child = pointer + "/" + name.replace("~", "~0").replace("/", "~1")
                if name.startswith("."):
                    if name != "." and not name.startswith("./"):
                        flag("INVALID_EXPORT_KEY", "HIGH", child,
                             "Subpath keys must be '.' or begin './'.")
                    if name.startswith("./") and _invalid_segment(name):
                        flag("INVALID_EXPORT_KEY", "HIGH", child,
                             "Subpath key has invalid or unsafe segments.")
                walk(entry, child, key=name if name.startswith(".") else key)
            return
        flag("INVALID_TARGET_TYPE", "HIGH", pointer,
             "Export mapping target is not a supported string, null, list or object.")
    walk(exports, "/exports")
    findings.sort(key=lambda item: (item["location"], item["code"]))
    return findings, target_count

def audit(path, check_files=False):
    given = Path(path)
    if given.is_symlink():
        raise InputError("symlink input refused")
    package = given / "package.json" if given.is_dir() else given
    if package.name != "package.json" or package.is_symlink() or not package.is_file():
        raise InputError("expected regular package.json file or package directory")
    if package.stat().st_size > MAX_BYTES:
        raise InputError("package.json exceeds 2 MB limit")
    try:
        obj = json.loads(package.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    except (ValueError, OSError, UnicodeError) as exc:
        raise InputError("invalid package.json JSON") from exc
    if not isinstance(obj, dict):
        raise InputError("package.json must be a JSON object")
    if "exports" not in obj:
        return {"package": package.name, "exports_present": False, "targets": 0, "findings": [],
                "summary": {"HIGH": 0, "REVIEW": 0}}
    findings, count = inspect_exports(obj["exports"], package.parent, check_files=check_files)
    return {"package": package.name, "exports_present": True, "targets": count,
            "findings": findings,
            "summary": {"HIGH": sum(f["severity"] == "HIGH" for f in findings),
                        "REVIEW": sum(f["severity"] == "REVIEW" for f in findings)}}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="package.json file or containing directory")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("high", "review", "never"), default="high")
    parser.add_argument("--check-files", action="store_true",
                        help="report unbuilt/missing output files as REVIEW")
    args = parser.parse_args(argv)
    try:
        result = audit(args.package, check_files=args.check_files)
    except (OSError, InputError) as exc:
        print("INPUT_ERROR: " + str(exc), file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Exports present: %s; targets: %s" % (result["exports_present"], result["targets"]))
        for f in result["findings"]:
            print("%s %s %s: %s" % (f["severity"], f["code"], f["location"], f["detail"]))
        if not result["findings"]:
            print("No modelled findings; Node.js runtime resolution was not executed.")
    if args.fail_on == "never":
        return 0
    if args.fail_on == "high":
        return int(result["summary"]["HIGH"] > 0)
    return int(bool(result["findings"]))

if __name__ == "__main__":
    sys.exit(main())
