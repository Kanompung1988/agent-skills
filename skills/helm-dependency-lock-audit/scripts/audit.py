#!/usr/bin/env python3
"""Read-only Helm Chart.yaml/Chart.lock dependency contract audit."""
import argparse
import json
import pathlib
import sys
import yaml

FILE_LIMIT = 1024 * 1024
MAX_FILES = 100


def entries(obj):
    if not isinstance(obj, dict):
        raise ValueError("Expected YAML mapping")
    rows = obj.get("dependencies") or []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("dependencies must be a list of objects")
    return rows


def identity(row):
    return (row.get("name"), row.get("repository"))


def audit(chart, lock, path):
    findings = []
    resource = str(path)
    def flag(code, sev, msg, fix):
        findings.append(dict(code=code, severity=sev, file=resource, resource="Helm chart dependencies",
                             message=msg, remediation=fix))
    declared = entries(chart)
    if not declared:
        if lock and entries(lock):
            flag("HL005", "review", "Chart.lock contains dependencies but Chart.yaml declares none.", "Review obsolete lock.")
        return findings
    if lock is None:
        flag("HL001", "review", "Chart.yaml declares dependencies but Chart.lock is missing.", "Run helm dependency update, commit Chart.lock, then helm dependency build.")
        return findings
    pinned = entries(lock)
    from collections import Counter
    requested = Counter(identity(x) for x in declared)
    locked = Counter(identity(x) for x in pinned)
    for key, count in requested.items():
        if count > 1:
            flag("HL002", "review", "Repeated dependency name/repository declaration.", "Disambiguate dependencies with unique names/aliases.")
        if locked[key] < count:
            flag("HL003", "review", "Chart.yaml dependency is absent or under-counted in Chart.lock.", "Reconcile lock with helm dependency update.")
    for key, count in locked.items():
        if count > requested[key]:
            flag("HL004", "review", "Chart.lock includes dependency not matching a declared name/repository.", "Rebuild lock with Helm and review repository URL changes.")
    for item in declared:
        version = item.get("version")
        if not isinstance(item.get("name"), str) or not item.get("name"):
            flag("HL006", "error", "Dependency has no name.", "Set dependency name.")
        if not isinstance(version, str) or not version:
            flag("HL007", "error", "Dependency has no version constraint.", "Set a valid version or range.")
        if not isinstance(item.get("repository"), str) or not item.get("repository"):
            flag("HL008", "review", "Dependency repository not declared.", "Specify repository or validate vendored chart workflow.")
        if isinstance(version, str) and version and all(c.isdigit() or c=="." or c=="-" or c=="+" or c.isalpha() for c in version):
            candidates = [p for p in pinned if identity(p) == identity(item)]
            if candidates and version[0].isdigit() and version != candidates[0].get("version"):
                flag("HL009", "review", "Exact Chart.yaml dependency version differs from locked version.", "Update lock and rebuild dependencies.")
    if not isinstance(lock.get("digest"), str) or not lock["digest"].startswith("sha256:"):
        flag("HL010", "review", "Chart.lock digest absent or not sha256-prefixed.", "Regenerate lock using helm dependency update.")
    if not isinstance(lock.get("generated"), (str, __import__("datetime").datetime)):
        flag("HL011", "review", "Chart.lock generated timestamp absent.", "Regenerate with Helm.")
    return findings


def read_yaml(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > FILE_LIMIT:
        raise ValueError("Must be a regular YAML file <= 1 MiB (no symlinks)")
    try:
        obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeError) as exc:
        raise ValueError("Invalid YAML file") from exc
    if not isinstance(obj, dict):
        raise ValueError("Expected YAML mapping")
    return obj


def charts(path):
    root = pathlib.Path(path)
    if root.is_symlink():
        raise ValueError("Symlink inputs are not allowed")
    if root.is_file():
        if root.name != "Chart.yaml":
            raise ValueError("Pass a Chart.yaml file or chart directory")
        return [root]
    if not root.is_dir():
        raise ValueError("Input must be Chart.yaml or directory")
    result = sorted(p for p in root.rglob("Chart.yaml") if p.is_file())
    if len(result) > MAX_FILES or any(p.is_symlink() for p in result):
        raise ValueError("Too many charts or symlink inputs")
    return result


def run(path):
    output = []
    selected = charts(path)
    if not selected:
        raise ValueError("No Chart.yaml found")
    for chart_path in selected:
        chart = read_yaml(chart_path)
        lock_path = chart_path.with_name("Chart.lock")
        lock = read_yaml(lock_path) if lock_path.exists() else None
        output.extend(audit(chart, lock, chart_path))
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Helm chart directory or Chart.yaml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        findings = run(args.path)
    except (ValueError, OSError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        for item in findings:
            print(f"{item['code']} {item['file']}: {item['message']}")
        print(f"Findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
