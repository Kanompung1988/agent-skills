#!/usr/bin/env python3
"""Read-only Kubernetes topology spread static checks; not scheduler simulation."""
import argparse
import json
import pathlib
import sys
import yaml

KINDS = {"Pod", "Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Job", "CronJob"}
FILE_LIMIT = 1024 * 1024
MAX_FILES = 100


def pod_of(obj):
    kind = obj.get("kind")
    spec = obj.get("spec") or {}
    if not isinstance(spec, dict) or kind not in KINDS:
        return None
    if kind == "Pod":
        return obj.get("metadata") or {}, spec
    if kind == "CronJob":
        spec = (((spec.get("jobTemplate") or {}).get("spec") or {}).get("template") or {})
    elif kind in KINDS:
        spec = spec.get("template") or {}
    if not isinstance(spec, dict):
        return None
    return spec.get("metadata") or {}, spec.get("spec") or {}


def matches(selector, labels):
    """True / False / None (unknown / invalid selector)."""
    if not isinstance(selector, dict) or not isinstance(labels, dict):
        return None
    conditions = selector.get("matchLabels") or {}
    if not isinstance(conditions, dict):
        return None
    if any(labels.get(k) != v for k, v in conditions.items()):
        return False
    for exp in selector.get("matchExpressions") or []:
        if not isinstance(exp, dict):
            return None
        key, op, values = exp.get("key"), exp.get("operator"), exp.get("values", [])
        if not isinstance(key, str) or not isinstance(values, list):
            return None
        if op == "In" and (not values or labels.get(key) not in values):
            return False
        if op == "NotIn" and (not values or (key in labels and labels[key] in values) or key not in labels):
            return False
        if op == "Exists" and key not in labels:
            return False
        if op == "DoesNotExist" and key in labels:
            return False
        if op not in ("In", "NotIn", "Exists", "DoesNotExist"):
            return None
    return True


def audit_documents(documents, filename="<memory>"):
    findings = []
    def flag(code, severity, resource, message, remediation):
        findings.append(dict(code=code, severity=severity, resource=resource,
                             file=filename, message=message, remediation=remediation))
    for obj in documents:
        if not isinstance(obj, dict):
            continue
        kind = obj.get("kind")
        if kind not in KINDS:
            continue
        meta = obj.get("metadata") or {}
        resource = f"{kind}/{meta.get('name', '<unnamed>')}"
        pod = pod_of(obj)
        if not pod:
            continue
        podmeta, pods = pod
        if not isinstance(pods, dict):
            flag("TS000", "error", resource, "Pod template spec is not a map.", "Correct the workload template.")
            continue
        labels = (podmeta or {}).get("labels") or {}
        constraints = pods.get("topologySpreadConstraints") or []
        if not isinstance(constraints, list):
            flag("TS000", "error", resource, "topologySpreadConstraints is not a list.", "Use a list of constraints.")
            continue
        seen = set()
        for i, entry in enumerate(constraints):
            loc = f"{resource} constraint[{i}]"
            if not isinstance(entry, dict):
                flag("TS000", "error", loc, "Constraint is not a map.", "Provide a valid constraint map.")
                continue
            skew = entry.get("maxSkew")
            if type(skew) is not int or skew < 1:
                flag("TS001", "error", loc, "maxSkew must be a positive integer.", "Set maxSkew to >= 1.")
            key = entry.get("topologyKey")
            if not isinstance(key, str) or not key.strip():
                flag("TS002", "error", loc, "topologyKey is missing.", "Use a node topology label key.")
            mode = entry.get("whenUnsatisfiable", "DoNotSchedule")
            if mode not in ("DoNotSchedule", "ScheduleAnyway"):
                flag("TS003", "error", loc, "Unknown whenUnsatisfiable value.", "Use DoNotSchedule or ScheduleAnyway.")
            if "minDomains" in entry:
                n = entry["minDomains"]
                if type(n) is not int or n < 1 or mode != "DoNotSchedule":
                    flag("TS004", "error", loc, "minDomains requires positive integer and DoNotSchedule.", "Correct minDomains/mode.")
            for name in ("nodeAffinityPolicy", "nodeTaintsPolicy"):
                if name in entry and entry[name] not in ("Honor", "Ignore"):
                    flag("TS005", "error", loc, f"{name} must be Honor or Ignore.", "Correct node inclusion policy.")
            selector = entry.get("labelSelector")
            match_keys = entry.get("matchLabelKeys") or []
            if match_keys:
                if not isinstance(match_keys, list) or not all(isinstance(k, str) for k in match_keys):
                    flag("TS006", "error", loc, "matchLabelKeys must be a list of label keys.", "Correct matchLabelKeys.")
                else:
                    selector_labels = (selector or {}).get("matchLabels") if isinstance(selector, dict) else {}
                    if selector is None:
                        flag("TS006", "error", loc, "matchLabelKeys requires labelSelector.", "Specify a labelSelector.")
                    if isinstance(selector_labels, dict) and any(k in selector_labels for k in match_keys):
                        flag("TS007", "error", loc, "Label key appears in matchLabelKeys and matchLabels.", "Remove duplicate key.")
                    if isinstance(labels, dict):
                        for k in match_keys:
                            if k not in labels:
                                flag("TS008", "review", loc, "A matchLabelKeys key is not in this Pod template labels.", "Verify generated pod labels and rollout timing.")
            if selector is None:
                flag("TS009", "review", loc, "No labelSelector supplied; matching pod counts may be zero.", "Set a deliberate selector for the pods to spread.")
            else:
                result = matches(selector, labels)
                if result is None:
                    flag("TS010", "error", loc, "Unsupported/malformed label selector.", "Validate selector operators and values.")
                elif result is False and not match_keys:
                    flag("TS011", "review", loc, "Label selector does not match this Pod template.", "Review whether self-exclusion is intended.")
            signature = json.dumps(entry, sort_keys=True)
            if signature in seen:
                flag("TS012", "review", loc, "Identical topology spread constraint repeated.", "Remove duplicate if unintended.")
            seen.add(signature)
    return findings


def paths(target):
    path = pathlib.Path(target)
    if path.is_symlink():
        raise ValueError("Symlink inputs are not allowed")
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError("Input must be a local file or directory")
    files = sorted(p for p in path.rglob("*") if p.suffix in (".yaml", ".yml") and p.is_file())
    if any(p.is_symlink() for p in files) or len(files) > MAX_FILES:
        raise ValueError("Symlink or too many YAML files")
    return files


def run(target):
    all_findings = []
    files = paths(target)
    if not files:
        raise ValueError("No YAML input files")
    for file in files:
        if file.stat().st_size > FILE_LIMIT:
            raise ValueError("Input exceeds 1 MiB file limit")
        try:
            docs = list(yaml.safe_load_all(file.read_text(encoding="utf-8")))
        except (yaml.YAMLError, UnicodeError) as exc:
            raise ValueError("Invalid YAML input") from exc
        all_findings.extend(audit_documents(docs, str(file)))
    return all_findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
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
        for f in findings:
            print(f"{f['code']} {f['resource']}: {f['message']}")
        print(f"Findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
