"""Offline Dockerfile ARG/ENV credentials and BuildKit secret mount boundary review."""
import argparse
import json
import re
import sys
from pathlib import Path

SECRET_NAME = re.compile(r"(?:secret|password|passwd|token|credential|api[_-]?key|private[_-]?key|access[_-]?key)", re.I)
SHELL_VAR = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")
MOUNT = re.compile(r"--mount=([^\s]+)")

def logical(text):
    pending, start = "", 1
    for n, row in enumerate(text.splitlines(), 1):
        if not pending:
            start = n
        row = row.rstrip()
        if row.endswith("\\"):
            pending += row[:-1] + " "
            continue
        merged = (pending + row).strip()
        pending = ""
        if merged and not merged.startswith("#"):
            yield start, merged
    if pending.strip():
        yield start, pending.strip()

def sensitive(name):
    return bool(SECRET_NAME.search(name)) and not re.search(r"public[_-]?key|tokenizer|secretary", name, re.I)

def analyze(text, path="Dockerfile"):
    findings = []
    declared = set()
    def note(code, line, message):
        findings.append({"code": code, "line": line, "path": str(path), "detail": message})
    for line, logical_line in logical(text):
        match = re.match(r"^([A-Za-z]+)\s+(.*)$", logical_line, re.S)
        if not match:
            continue
        command, rest = match.group(1).upper(), match.group(2)
        if command == "ARG":
            name_match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", rest)
            if name_match and sensitive(name_match.group(1)):
                declared.add(name_match.group(1))
                note("BS001", line, "sensitive-looking ARG name " + name_match.group(1) + " (value redacted)")
        elif command == "ENV":
            names = re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)\s*=", rest)
            if not names:
                old = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s+", rest)
                names = [old.group(1)] if old else []
            for name in names:
                if sensitive(name):
                    declared.add(name)
                    note("BS002", line, "sensitive-looking ENV name " + name + " (value redacted)")
        elif command == "RUN":
            mounts = [m.group(1) for m in MOUNT.finditer(rest) if m.group(1).startswith("type=secret")]
            ids = set()
            envs = set()
            paths = set()
            for mount in mounts:
                pairs = {}
                for piece in mount.split(","):
                    if "=" in piece:
                        k, v = piece.split("=", 1)
                        pairs[k] = v
                if pairs.get("id"):
                    ids.add(pairs["id"])
                if pairs.get("env"):
                    envs.add(pairs["env"])
                if pairs.get("target"):
                    paths.add(pairs["target"])
                if pairs.get("required", "false").lower() != "true":
                    note("BS003", line, "optional secret mount (required=true not set)")
                if not pairs.get("id") and not pairs.get("target"):
                    note("BS004", line, "secret mount missing id and target")
            for name in set(re.findall(r"/run/secrets/([A-Za-z0-9_.-]+)", rest)):
                if name not in ids and "/run/secrets/" + name not in paths:
                    note("BS005", line, "RUN reads /run/secrets/" + name + " without same-RUN matching mount")
            for var in set(a or b for a, b in SHELL_VAR.findall(rest)):
                if var in declared:
                    note("BS006", line, "RUN reads sensitive ARG/ENV name " + var)
            for name in envs:
                if name in declared:
                    note("BS007", line, "BuildKit secret env " + name + " also declared via ARG/ENV")
    return sorted(findings, key=lambda x: (x["line"], x["code"], x["detail"]))

def scan(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 2_000_000:
        raise ValueError("expected existing regular Dockerfile <= 2MB")
    return analyze(path.read_text(encoding="utf-8"), path)

def main(argv=None):
    p = argparse.ArgumentParser(description="Offline BuildKit secret boundary review")
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    try:
        findings = scan(args.path)
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc)}) if args.json else str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        for item in findings:
            print(f'{item["path"]}:{item["line"]} {item["code"]}: {item["detail"]}')
    return 1 if findings else 0

if __name__ == "__main__":
    sys.exit(main())
