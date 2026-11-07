#!/usr/bin/env python3
"""Offline hardening review for rendered Kubernetes workload YAML.

Read-only. Findings are a review checklist, not an admission-policy verdict.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

WORKLOAD_PATHS = {
    "Pod": (),
    "Deployment": ("spec", "template"),
    "StatefulSet": ("spec", "template"),
    "DaemonSet": ("spec", "template"),
    "ReplicaSet": ("spec", "template"),
    "Job": ("spec", "template"),
    "CronJob": ("spec", "jobTemplate", "spec", "template"),
    "ReplicationController": ("spec", "template"),
}

def mapping(value):
    return value if isinstance(value, dict) else {}

def pod_specs(item):
    """Yield (resource identifier, pod spec) for recognized rendered workloads."""
    if not isinstance(item, dict):
        raise ValueError("Each YAML document or List item must be a mapping")
    if item.get("kind") == "List":
        entries = item.get("items")
        if not isinstance(entries, list):
            raise ValueError("List.items must be a list")
        for child in entries:
            yield from pod_specs(child)
        return
    kind = item.get("kind")
    if kind not in WORKLOAD_PATHS:
        return
    namespace = mapping(item.get("metadata")).get("namespace", "default")
    name = mapping(item.get("metadata")).get("name", "<unnamed>")
    path = WORKLOAD_PATHS[kind]
    node = item
    for part in path:
        node = mapping(node).get(part)
    spec = mapping(node).get("spec") if path else item.get("spec")
    if not isinstance(spec, dict):
        raise ValueError(f"{kind}/{name} is missing a valid Pod spec")
    yield f"{namespace}/{kind}/{name}", spec

def inspect_document(resource, pod):
    findings = []
    def flag(code, location, severity, message):
        findings.append(dict(code=code, resource=resource, location=location,
                             severity=severity, message=message))
    podsc = mapping(pod.get("securityContext"))
    windows = mapping(pod.get("os")).get("name", "").lower() == "windows"
    if pod.get("hostNetwork") is True:
        flag("HOST_NETWORK", "spec.hostNetwork", "review", "Host network is shared with the node")
    if pod.get("hostPID") is True or pod.get("hostIPC") is True:
        flag("HOST_NAMESPACE", "spec", "review", "Host PID or IPC namespace is enabled")
    types = ("containers", "initContainers", "ephemeralContainers")
    count = 0
    for group in types:
        members = pod.get(group, [])
        if members is None:
            members = []
        if not isinstance(members, list):
            raise ValueError(f"{resource}: {group} must be a list")
        for pos, ctr in enumerate(members):
            if not isinstance(ctr, dict):
                raise ValueError(f"{resource}: {group}[{pos}] must be a mapping")
            count += 1
            label = str(ctr.get("name") or pos)
            loc = f"spec.{group}[{label}]"
            sc = mapping(ctr.get("securityContext"))
            if sc.get("privileged") is True:
                flag("PRIVILEGED", loc, "high", "Privileged container bypasses important isolation")
            if windows:
                if mapping(sc.get("windowsOptions")).get("hostProcess") is True or mapping(podsc.get("windowsOptions")).get("hostProcess") is True:
                    flag("WINDOWS_HOST_PROCESS", loc, "high", "Windows HostProcess container requested")
                continue
            if sc.get("allowPrivilegeEscalation") is not False:
                flag("PRIVILEGE_ESCALATION", loc, "high", "Set allowPrivilegeEscalation: false for Linux hardening")
            effective_nonroot = sc.get("runAsNonRoot", podsc.get("runAsNonRoot"))
            effective_user = sc.get("runAsUser", podsc.get("runAsUser"))
            if effective_user == 0:
                flag("ROOT_UID", loc, "high", "Effective runAsUser is 0")
            if effective_nonroot is not True:
                flag("NONROOT_UNSET", loc, "review", "No effective runAsNonRoot: true")
            caps = mapping(sc.get("capabilities"))
            drops = caps.get("drop") or []
            adds = caps.get("add") or []
            if not isinstance(drops, list) or not isinstance(adds, list):
                raise ValueError(f"{resource}: capabilities add/drop must be lists")
            if "ALL" not in drops:
                flag("CAPABILITIES_DROP", loc, "review", "Linux container does not explicitly drop ALL capabilities")
            other = [str(x) for x in adds if x not in ("NET_BIND_SERVICE",)]
            if other:
                flag("CAPABILITIES_ADD", loc, "high", "Linux container adds capability beyond NET_BIND_SERVICE")
            seccomp = mapping(sc.get("seccompProfile")).get("type")
            if seccomp is None:
                seccomp = mapping(podsc.get("seccompProfile")).get("type")
            if seccomp not in ("RuntimeDefault", "Localhost"):
                flag("SECCOMP", loc, "review", "No effective RuntimeDefault or Localhost seccomp profile")
            if sc.get("readOnlyRootFilesystem") is not True:
                flag("WRITABLE_ROOT", loc, "advisory", "Consider readOnlyRootFilesystem: true (hardening recommendation, not PSS Restricted requirement)")
    if count == 0:
        raise ValueError(f"{resource}: no container entries to inspect")
    return findings

def audit(path):
    text = Path(path).read_text(encoding="utf-8")
    findings, inspected = [], 0
    for item in yaml.safe_load_all(text):
        if item is None:
            continue
        for resource, pod in pod_specs(item):
            inspected += 1
            findings.extend(inspect_document(resource, pod))
    return {"inspected": inspected, "count": len(findings), "findings": findings,
            "note": "Static review of supplied rendered manifests; not an admission-controller or live-cluster verdict"}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", help="Local rendered YAML document(s), no cluster access")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args(argv)
    try:
        result = audit(args.manifest)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Inspected {result['inspected']} workloads; {result['count']} findings")
        for f in result["findings"]:
            print(f"{f['severity']}: {f['resource']} {f['location']} {f['code']}: {f['message']}")
    return 1 if result["count"] else 0

if __name__ == "__main__":
    sys.exit(main())
