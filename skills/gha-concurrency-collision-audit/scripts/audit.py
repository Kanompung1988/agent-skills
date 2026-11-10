"""Offline GitHub Actions workflow/job concurrency group review."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml

EXPRESSION = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")

def normalize(value):
    if not isinstance(value, str):
        return ""
    return EXPRESSION.sub(lambda m: "${{ " + " ".join(m.group(1).split()) + " }}", value.strip()).casefold()

def events(doc):
    value = doc.get("on", doc.get(True))
    if isinstance(value, str): return {value}
    if isinstance(value, (list, dict)): return set(map(str, value))
    return set()

def analyze(docs):
    findings, groups = [], {}
    def report(code, file, where, detail):
        findings.append({"code": code, "path": str(file), "location": where, "detail": detail})
    for file, doc in sorted(docs.items(), key=lambda x: str(x[0])):
        if not isinstance(doc, dict):
            raise ValueError(f"{file}: expected YAML mapping")
        jobs = doc.get("jobs") or {}
        if not isinstance(jobs, dict):
            raise ValueError(f"{file}: jobs must be a mapping")
        scopes = [("workflow", doc.get("concurrency"))]
        scopes.extend((f"jobs.{name}", job.get("concurrency")) for name, job in jobs.items() if isinstance(job, dict))
        for where, value in scopes:
            if value is None: continue
            item = {"group": value} if isinstance(value, str) else value
            if not isinstance(item, dict) or not normalize(item.get("group")):
                report("CC001", file, where, "invalid or missing concurrency group")
                continue
            group = normalize(item["group"])
            groups.setdefault(group, []).append((file, where))
            cancel, queue = item.get("cancel-in-progress", False), item.get("queue", "single")
            if queue == "max" and cancel is True:
                report("CC002", file, where, "queue max incompatible with cancel-in-progress true")
            if "github.head_ref" in group and ("push" in events(doc) or "workflow_dispatch" in events(doc)) and "||" not in group:
                report("CC003", file, where, "head_ref may be undefined; add fallback")
            if cancel is True and re.search(r"release|deploy|publish|production", file.name + " " + str(doc.get("name", "")), re.I):
                report("CC004", file, where, "unconditional cancellation in release or deployment workflow")
            if group in {"${{ github.ref }}", "${{ github.head_ref }}"}:
                report("CC005", file, where, "concurrency group missing workflow identity")
            if isinstance(cancel, str) and not EXPRESSION.search(cancel):
                report("CC006", file, where, "cancel-in-progress neither boolean nor expression")
            if queue not in ("single", "max"):
                report("CC007", file, where, "queue must be single or max")
    for group, members in groups.items():
        if len(members) > 1:
            code = "CC008" if len({str(file) for file, _ in members}) > 1 else "CC009"
            for file, where in members:
                report(code, file, where, "group shared by multiple scopes; confirm cancellation is intentional")
    return sorted(findings, key=lambda f: (f["path"], f["location"], f["code"]))

def scan(input_path):
    root = Path(input_path)
    if root.is_file():
        files = [root]
    elif root.is_dir():
        files = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".yaml", ".yml"} and p.is_file())
    else:
        raise ValueError("input path missing")
    if not files: raise ValueError("no YAML files found")
    docs = {}
    for file in files:
        if file.is_symlink() or file.stat().st_size > 2000000:
            raise ValueError("symlink or oversized workflow not allowed")
        docs[file] = yaml.safe_load(file.read_text(encoding="utf-8"))
    return analyze(docs)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only workflow concurrency collision review")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        findings = scan(args.path)
    except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
        print(json.dumps({"error": str(exc)}) if args.json else str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        for finding in findings:
            print(f'{finding["path"]} {finding["location"]}: {finding["code"]}: {finding["detail"]}')
    return 1 if findings else 0

if __name__ == "__main__":
    sys.exit(main())
