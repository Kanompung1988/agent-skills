#!/usr/bin/env python3
"""Read-only heuristic review of GitHub Actions attestation gates."""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: python -m pip install 'PyYAML>=6,<7'")

MAX_BYTES = 1024 * 1024
MAX_FILES = 100
VERIFY = re.compile(r"(?<![A-Za-z0-9_])gh\s+attestation\s+verify(?:\s|$)", re.I)
REPO_FLAG = re.compile(r"(?<!\S)(?:-R|-o|--repo|--owner)(?:\s|=)")
ALWAYS_TRUE = {"true", "True", True}


def item(rule, file, job, detail):
    return {"rule": rule, "file": file, "job": str(job), "message": detail}


def audit_workflow(data, filename):
    if not isinstance(data, dict):
        raise ValueError("workflow must be a YAML mapping")
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        raise ValueError("workflow jobs must be a mapping")
    results = []
    for name, job in jobs.items():
        if not isinstance(job, dict):
            raise ValueError("each job must be a mapping")
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError("job steps must be a list")
        effective = job.get("permissions", data.get("permissions", {}))
        if not isinstance(effective, dict):
            effective = {}
        attests, verifications, downloads = [], [], []
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError("steps must be mappings")
            uses = str(step.get("uses", ""))
            if re.match(r"^actions/attest@", uses, re.I):
                attests.append((index, step))
            if re.match(r"^(?:actions/download-artifact|softprops/action-gh-release)@", uses, re.I):
                downloads.append(index)
            run = step.get("run", "")
            if not isinstance(run, str):
                continue
            # Ignore plain shell comments; quoted/commented code, composite actions and wrappers
            # remain outside the scanner's static proof boundary.
            commands = "\n".join(line for line in run.splitlines()
                                 if not line.lstrip().startswith("#"))
            if VERIFY.search(commands):
                verifications.append((index, step, commands))
        for index, step in attests:
            if effective.get("id-token") != "write":
                results.append(item("AA001", filename, name,
                                    "actions/attest needs effective id-token: write"))
            if effective.get("attestations") != "write":
                results.append(item("AA002", filename, name,
                                    "actions/attest needs effective attestations: write"))
            opts = step.get("with", {})
            if not isinstance(opts, dict):
                opts = {}
            if bool(opts.get("subject-name")) != bool(opts.get("subject-digest")):
                results.append(item("AA003", filename, name,
                                    "image subject-name and subject-digest should be supplied together"))
            if not any(key in opts for key in
                       ("subject-path", "subject-digest", "subject-checksums")):
                results.append(item("AA004", filename, name,
                                    "attestation relies on implicit subject discovery; confirm intended artifacts"))
        for index, step, command in verifications:
            if not REPO_FLAG.search(command):
                results.append(item("AA005", filename, name,
                                    "gh attestation verify has no visible --repo/-R or --owner/-o trust scope"))
            if step.get("continue-on-error") in ALWAYS_TRUE:
                results.append(item("AA006", filename, name,
                                    "verification step uses continue-on-error: true"))
            if re.search(r"\|\|\s*true(?:\s|$|[;&])", command):
                results.append(item("AA007", filename, name,
                                    "verification includes a fail-open '|| true' pattern"))
        if downloads and not verifications:
            results.append(item("AA008", filename, name,
                                "download/release step has no visible gh attestation verify in this job"))
        # Same-job order is worth a manual audit even when a verify exists.
        if downloads and verifications and min(i for i, _, _ in verifications) < max(downloads):
            results.append(item("AA009", filename, name,
                                "verification appears before at least one download step; check subject ordering"))
    return results


def audit_path(target):
    path = Path(target)
    if path.is_symlink():
        raise ValueError("symlink inputs are not followed")
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted([*path.glob("*.yml"), *path.glob("*.yaml")])
    else:
        raise ValueError("path does not exist")
    if not files or len(files) > MAX_FILES:
        raise ValueError("expected 1–100 YAML workflow files")
    findings = []
    for p in files:
        if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe or oversized workflow file")
        try:
            doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        except (UnicodeError, yaml.YAMLError) as exc:
            raise ValueError("malformed workflow YAML: " + p.name) from exc
        findings.extend(audit_workflow(doc, p.name))
    return {"count": len(findings),
            "findings": sorted(findings, key=lambda f:(f["file"], f["job"], f["rule"]))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="YAML workflow file or a directory of YAML files")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args(argv)
    try:
        result = audit_path(args.path)
    except (OSError, ValueError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("Attestation review findings:", result["count"])
        for f in result["findings"]:
            print("{file}: {job}: {rule}: {message}".format(**f))
    return 1 if result["count"] else 0


if __name__ == "__main__":
    sys.exit(main())
