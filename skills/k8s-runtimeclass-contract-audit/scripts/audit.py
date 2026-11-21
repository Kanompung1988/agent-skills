#!/usr/bin/env python3
"""Offline Kubernetes RuntimeClass and Pod scheduling contract auditor."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any
import yaml

NAME = "k8s-runtimeclass-contract-audit"
QUANTITY = re.compile(r"^[+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+|[numkKMGTPE]i?)?$")
POD_KINDS = {"Pod", "PodTemplate"}
TEMPLATE_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "ReplicationController", "Job"}

def finding(rule: str, severity: str, file: str, doc: int, message: str, subject: str = "") -> dict[str, Any]:
    item = {"rule": rule, "severity": severity, "file": file, "document": doc, "message": message}
    if subject: item["subject"] = subject
    return item

def pod_specs(obj: dict[str, Any]):
    kind = obj.get("kind")
    spec = obj.get("spec") or {}
    if kind == "Pod":
        yield spec
    elif kind == "PodTemplate":
        yield ((obj.get("template") or {}).get("spec") or {})
    elif kind in TEMPLATE_KINDS:
        yield ((spec.get("template") or {}).get("spec") or {})
    elif kind == "CronJob":
        yield (((spec.get("jobTemplate") or {}).get("spec") or {}).get("template") or {}).get("spec") or {}
    elif kind in {"PodList", "List"}:
        for item in obj.get("items") or []:
            if isinstance(item, dict): yield from pod_specs(item)

def audit_documents(documents: list[Any], file: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    runtime_classes: dict[str, tuple[dict[str, Any], int]] = {}
    workloads: list[tuple[dict[str, Any], int, dict[str, Any]]] = []
    for index, obj in enumerate(documents, 1):
        if not isinstance(obj, dict): continue
        if obj.get("kind") == "RuntimeClass":
            name = ((obj.get("metadata") or {}).get("name") or "")
            spec = obj.get("spec") or {}
            if not name:
                findings.append(finding("RUNTIMECLASS_NAME_REQUIRED", "ERROR", file, index, "RuntimeClass metadata.name is required"))
            elif name in runtime_classes:
                findings.append(finding("RUNTIMECLASS_DUPLICATE", "ERROR", file, index, f"RuntimeClass {name!r} is defined more than once", name))
            else:
                runtime_classes[name] = (obj, index)
            if not isinstance(spec.get("handler"), str) or not spec.get("handler", "").strip():
                findings.append(finding("RUNTIMECLASS_HANDLER_REQUIRED", "ERROR", file, index, "spec.handler must be a non-empty string", name))
            scheduling = spec.get("scheduling") or {}
            if not isinstance(scheduling, dict):
                findings.append(finding("RUNTIMECLASS_SCHEDULING_INVALID", "ERROR", file, index, "spec.scheduling must be an object", name))
                scheduling = {}
            selector = scheduling.get("nodeSelector", {})
            if selector is not None and (not isinstance(selector, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in selector.items())):
                findings.append(finding("RUNTIMECLASS_NODESELECTOR_INVALID", "ERROR", file, index, "spec.scheduling.nodeSelector must be a string-to-string map", name))
            tolerations = scheduling.get("tolerations", []) if isinstance(scheduling, dict) else []
            if tolerations is not None and not isinstance(tolerations, list):
                findings.append(finding("RUNTIMECLASS_TOLERATIONS_INVALID", "ERROR", file, index, "spec.scheduling.tolerations must be a list", name))
            overhead = spec.get("overhead") or {}
            if not isinstance(overhead, dict):
                findings.append(finding("RUNTIMECLASS_OVERHEAD_INVALID", "ERROR", file, index, "spec.overhead must be an object", name))
                overhead = {}
            pod_fixed = overhead.get("podFixed", {})
            if pod_fixed is not None and not isinstance(pod_fixed, dict):
                findings.append(finding("RUNTIMECLASS_OVERHEAD_INVALID", "ERROR", file, index, "spec.overhead.podFixed must be a resource-quantity map", name))
            elif isinstance(pod_fixed, dict):
                for resource, quantity in pod_fixed.items():
                    if not isinstance(resource, str) or not isinstance(quantity, (str, int, float)) or isinstance(quantity, bool) or not QUANTITY.fullmatch(str(quantity)):
                        findings.append(finding("RUNTIMECLASS_OVERHEAD_QUANTITY_INVALID", "ERROR", file, index, f"overhead quantity for {resource!r} is not a supported non-negative Kubernetes quantity", name))
        for pod_spec in pod_specs(obj):
            workloads.append((pod_spec, index, obj))
    for pod_spec, index, obj in workloads:
        runtime_name = pod_spec.get("runtimeClassName")
        if not runtime_name: continue
        pod_selector = pod_spec.get("nodeSelector", {})
        if not isinstance(pod_selector, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in pod_selector.items()):
            findings.append(finding("POD_NODESELECTOR_INVALID", "ERROR", file, index, "Pod spec.nodeSelector must be a string-to-string map", str(runtime_name)))
            pod_selector = {}
        if runtime_name not in runtime_classes:
            findings.append(finding("RUNTIMECLASS_EXTERNAL_REFERENCE", "INFO", file, index, f"Pod references RuntimeClass {runtime_name!r}, which is not defined in the supplied files; it may exist in the cluster", str(runtime_name)))
            continue
        runtime_obj, rc_doc = runtime_classes[runtime_name]
        rc_selector = (((runtime_obj.get("spec") or {}).get("scheduling") or {}).get("nodeSelector") or {})
        if isinstance(rc_selector, dict) and isinstance(pod_selector, dict):
            for key in sorted(set(rc_selector) & set(pod_selector)):
                if rc_selector[key] != pod_selector[key]:
                    findings.append(finding("RUNTIMECLASS_NODESELECTOR_CONFLICT", "ERROR", file, index, f"RuntimeClass {runtime_name!r} requires {key}={rc_selector[key]!r}, but the Pod requires {key}={pod_selector[key]!r}; admission rejects the merged selectors", str(runtime_name)))
    return findings

def audit_file(path: Path) -> list[dict[str, Any]]:
    try:
        docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return [finding("INPUT_PARSE_ERROR", "ERROR", str(path), 0, f"Cannot safely parse YAML: {exc}")]
    return audit_documents(docs, str(path))

def collect(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir(): out.extend(sorted(x for x in p.rglob("*") if x.suffix.lower() in {".yaml", ".yml"}))
        else: out.append(p)
    return out

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Kubernetes RuntimeClass scheduling/overhead contract audit")
    parser.add_argument("paths", nargs="+", help="YAML files or directories")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error")
    args = parser.parse_args(argv)
    files = collect(args.paths)
    if not files:
        print("No YAML files found", file=sys.stderr); return 1
    findings = [f for path in files for f in audit_file(path)]
    if args.format == "json": print(json.dumps({"tool": NAME, "findings": findings}, indent=2))
    else:
        for f in findings: print(f"{f['severity']}: {f['rule']}: {f['file']}#{f['document']}: {f['message']}")
        print(f"Reviewed {len(files)} file(s); {len(findings)} finding(s)")
    if args.fail_on == "never": return 0
    threshold = {"error": {"ERROR"}, "warning": {"ERROR", "WARNING"}}[args.fail_on]
    return 2 if any(f["severity"] in threshold for f in findings) else 0

if __name__ == "__main__": raise SystemExit(main())
