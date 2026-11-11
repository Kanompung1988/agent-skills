#!/usr/bin/env python3
"""Read-only, bounded Kubernetes CronJob configuration checks."""
import argparse
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import datetime
import yaml

def finding(code, message, resource):
    return {"code": code, "message": message, "resource": resource}

def review(doc):
    if not isinstance(doc, dict) or doc.get("kind") != "CronJob":
        return []
    meta = doc.get("metadata") or {}
    spec = doc.get("spec") or {}
    if not isinstance(meta, dict) or not isinstance(spec, dict):
        raise ValueError("CronJob metadata/spec must be mappings")
    resource = str(meta.get("namespace", "default")) + "/" + str(meta.get("name", "<unnamed>"))
    out = []
    def add(code, message):
        out.append(finding(code, message, resource))
    schedule = spec.get("schedule")
    if not isinstance(schedule, str) or len(schedule.split()) != 5:
        add("CJ001", "Expected a five-field Kubernetes cron schedule (macros and full cron grammar are not parsed).")
    if isinstance(schedule, str) and ("TZ=" in schedule.upper() or "CRON_TZ=" in schedule.upper()):
        add("CJ002", "TZ/CRON_TZ inside schedule is not supported; use spec.timeZone.")
    tz = spec.get("timeZone")
    if not tz:
        add("CJ003", "No spec.timeZone; controller-manager local time zone determines schedule.")
    elif not isinstance(tz, str):
        add("CJ004", "spec.timeZone must be an IANA timezone string.")
    else:
        try:
            zone = ZoneInfo(tz)
        except (ZoneInfoNotFoundError, ValueError):
            add("CJ004", "Unknown timezone; confirm IANA zone availability on target cluster.")
        else:
            winter = datetime.datetime(2026, 1, 15, tzinfo=zone).utcoffset()
            summer = datetime.datetime(2026, 7, 15, tzinfo=zone).utcoffset()
            if winter != summer and isinstance(schedule, str) and len(schedule.split()) == 5:
                add("CJ005", "Timezone changes UTC offset seasonally; review daylight-saving gaps/duplicates for local schedule.")
    deadline = spec.get("startingDeadlineSeconds")
    if deadline is not None:
        if isinstance(deadline, bool) or not isinstance(deadline, int) or deadline < 0:
            add("CJ006", "startingDeadlineSeconds must be a nonnegative integer.")
        elif 0 <= deadline < 10:
            add("CJ007", "Deadline under ten seconds may miss executions due to controller polling.")
    policy = spec.get("concurrencyPolicy", "Allow")
    if policy not in ("Allow", "Forbid", "Replace"):
        add("CJ008", "Unsupported concurrencyPolicy; expected Allow, Forbid or Replace.")
    elif policy == "Replace":
        add("CJ009", "Replace may terminate an active Job; confirm interruption tolerance.")
    elif policy == "Forbid" and deadline is None:
        add("CJ010", "Forbid skips overlapping schedules; assess catch-up/deadline policy for long-running Jobs.")
    if spec.get("failedJobsHistoryLimit") == 0:
        add("CJ011", "No failed Job history retained; confirm diagnostic retention elsewhere.")
    if spec.get("suspend") is True:
        add("CJ012", "CronJob is suspended; confirm this is intentional.")
    return out

def collect(path):
    if path.is_symlink():
        raise ValueError("Refusing symlink input")
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError("Input does not exist")
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in (".yaml", ".yml") and p.is_file() and not p.is_symlink())

def analyze(path):
    findings = []
    scanned = 0
    for file in collect(Path(path)):
        if file.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("YAML exceeds 2 MiB: " + str(file))
        try:
            docs = list(yaml.safe_load_all(file.read_text(encoding="utf-8")))
        except (yaml.YAMLError, UnicodeDecodeError, OSError) as exc:
            raise ValueError("Cannot parse " + str(file) + ": " + str(exc)) from exc
        for index, doc in enumerate(docs, 1):
            scanned += 1
            for item in review(doc):
                findings.append({"file": str(file), "document": index, **item})
    return {"documents_scanned": scanned, "findings": findings}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="YAML file or directory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = analyze(args.path)
    except (ValueError, OSError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for item in result["findings"]:
            print(f'{item["file"]}:{item["document"]} {item["code"]}: {item["message"]}')
        print(f'{result["documents_scanned"]} documents scanned; {len(result["findings"])} findings')
    return 1 if result["findings"] else 0

if __name__ == "__main__":
    sys.exit(main())
