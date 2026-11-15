#!/usr/bin/env python3
"""Bounded, read-only Gateway API cross-namespace reference audit."""
import argparse
import json
import sys
from pathlib import Path

import yaml

GROUP = "gateway.networking.k8s.io"
ROUTES = {"HTTPRoute", "GRPCRoute", "TCPRoute", "TLSRoute", "UDPRoute"}
MAX_SIZE = 2 * 1024 * 1024
MAX_FILES = 500


def mapping(value):
    return value if isinstance(value, dict) else {}


def sequence(value):
    return value if isinstance(value, list) else []


def resource_id(obj):
    meta = mapping(obj.get("metadata"))
    return f'{obj.get("kind", "?")}/{meta.get("namespace") or "default"}/{meta.get("name") or "?"}'


def issue(code, severity, filename, obj, message, advice):
    return {"code": code, "severity": severity, "file": str(filename),
            "resource": resource_id(obj), "message": message, "remediation": advice}


def collect(path):
    root = Path(path)
    if not root.exists() or root.is_symlink():
        raise ValueError("input must be an existing non-symlink file or directory")
    if root.is_dir():
        files = sorted(f for f in root.rglob("*") if f.suffix.lower() in {".yaml", ".yml"} and f.is_file())
    else:
        files = [root]
    if not files or len(files) > MAX_FILES:
        raise ValueError("provide 1 to 500 YAML files")
    docs = []
    for file in files:
        if file.is_symlink() or file.stat().st_size > MAX_SIZE:
            raise ValueError(f"refusing symlink or file larger than 2MiB: {file}")
        try:
            with file.open(encoding="utf-8") as inp:
                for idx, value in enumerate(yaml.safe_load_all(inp), 1):
                    if value is None:
                        continue
                    if not isinstance(value, dict):
                        raise ValueError(f"{file} document {idx} must be an object")
                    docs.append((str(file), value))
        except (yaml.YAMLError, UnicodeError) as exc:
            raise ValueError(f"invalid YAML in {file}: {exc}") from exc
    return docs


def granted(grants, origin_ns, origin_kind, target_ns, target_group, target_kind, target_name):
    for _, grant in grants:
        if mapping(grant.get("metadata")).get("namespace", "default") != target_ns:
            continue
        spec = mapping(grant.get("spec"))
        from_match = any(
            mapping(f).get("group") == GROUP
            and mapping(f).get("kind") == origin_kind
            and mapping(f).get("namespace") == origin_ns
            for f in sequence(spec.get("from"))
        )
        to_match = any(
            mapping(t).get("group") == target_group
            and mapping(t).get("kind") == target_kind
            and (not mapping(t).get("name") or mapping(t).get("name") == target_name)
            for t in sequence(spec.get("to"))
        )
        if from_match and to_match:
            return True
    return False


def references(obj):
    """Yield (type, reference) for supported Gateway API cross-namespace fields."""
    kind = obj.get("kind")
    spec = mapping(obj.get("spec"))
    if kind in ROUTES:
        parents = sequence(spec.get("parentRefs"))
        # Service parentRefs are mesh-consumer scopes; applicability is controller-dependent.
        mesh_only = bool(parents) and all(
            mapping(p).get("kind", "Gateway") == "Service" for p in parents
        )
        if mesh_only:
            return
        for rule in sequence(spec.get("rules")):
            rule = mapping(rule)
            for backend in sequence(rule.get("backendRefs")):
                yield ("backend", mapping(backend))
            for filt in sequence(rule.get("filters")):
                f = mapping(filt)
                if f.get("type") == "RequestMirror":
                    mirror = mapping(f.get("requestMirror"))
                    if mirror.get("backendRef"):
                        yield ("backend", mapping(mirror["backendRef"]))
    if kind == "Gateway":
        for listener in sequence(spec.get("listeners")):
            tls = mapping(mapping(listener).get("tls"))
            for cert in sequence(tls.get("certificateRefs")):
                yield ("certificate", mapping(cert))


def inspect(docs):
    findings = []
    grants = [(file, obj) for file, obj in docs
              if obj.get("kind") == "ReferenceGrant" and str(obj.get("apiVersion", "")).startswith(GROUP + "/")]
    for file, obj in grants:
        spec = mapping(obj.get("spec"))
        if not sequence(spec.get("from")) or not sequence(spec.get("to")):
            findings.append(issue("RG002", "error", file, obj, "ReferenceGrant has empty from/to rules",
                                  "Declare explicit from and to permissions in the target namespace."))
        for t in sequence(spec.get("to")):
            if not mapping(t).get("kind") or "group" not in mapping(t):
                findings.append(issue("RG003", "warning", file, obj, "ReferenceGrant to entry has missing kind/group",
                                      "Specify the target API group (empty string for core Service/Secret) and kind."))
    for file, obj in docs:
        kind = obj.get("kind")
        if kind not in ROUTES | {"Gateway"} or not str(obj.get("apiVersion", "")).startswith(GROUP + "/"):
            continue
        origin_ns = mapping(obj.get("metadata")).get("namespace") or "default"
        for ref_type, ref in references(obj):
            target_ns = ref.get("namespace") or origin_ns
            if not isinstance(target_ns, str):
                findings.append(issue("RG004", "error", file, obj, "Non-string reference namespace",
                                      "Use a valid namespace string."))
                continue
            if target_ns == origin_ns:
                continue
            target_name = ref.get("name")
            target_kind = ref.get("kind") or ("Secret" if ref_type == "certificate" else "Service")
            target_group = ref.get("group")
            if target_group is None:
                target_group = ""
            if not isinstance(target_name, str) or not target_name:
                findings.append(issue("RG005", "error", file, obj, "Cross-namespace reference has no target name",
                                      "Set the backend/certificate name."))
                continue
            if not granted(grants, origin_ns, kind, target_ns, target_group, target_kind, target_name):
                label = f"{target_group or 'core'}/{target_kind}/{target_ns}/{target_name}"
                findings.append(issue("RG001", "error", file, obj,
                                      f"Cross-namespace {ref_type} {label} lacks a matching local ReferenceGrant",
                                      "Create a ReferenceGrant in the target namespace allowing this source namespace and kind; verify live resources."))
    return sorted(findings, key=lambda f: (f["file"], f["resource"], f["code"], f["message"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="YAML file or directory of rendered manifests")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        results = inspect(collect(args.path))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}) if args.json else f"Input error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"count": len(results), "findings": results}, indent=2))
    else:
        for item in results:
            print(f'{item["code"]} [{item["severity"]}] {item["resource"]}: {item["message"]}')
        print(f"Review findings: {len(results)}")
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
