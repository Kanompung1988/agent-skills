#!/usr/bin/env python3
"""Conservative offline audit of Docker Compose host port bindings. Never runs Docker."""
import argparse
import ipaddress
import json
import re
import sys
from pathlib import Path

import yaml


def finding(severity, code, service, index, message):
    return {"severity": severity, "code": code, "service": service,
            "entry": index, "message": message}


def address_class(ip):
    """Return loopback, wildcard, other, or dynamic; never resolve DNS."""
    if ip is None or ip == "":
        return "unspecified"
    if not isinstance(ip, str) or "${" in ip or "$" in ip:
        return "dynamic"
    if ip.startswith("[") and ip.endswith("]"):
        ip = ip[1:-1]
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return "dynamic"
    if address.is_unspecified:
        return "wildcard"
    if address.is_loopback:
        return "loopback"
    return "other"


def parse_short(value):
    """Parse documented [HOST_IP:]HOST_PORT:CONTAINER_PORT[/PROTO] with IPv6 bracket support.

    A single container port is published on an ephemeral host port. Syntax not
    confidently recognized is reported as review, never guessed as safe.
    """
    if isinstance(value, int) and not isinstance(value, bool):
        return (None, str(value), None)
    if not isinstance(value, str):
        return (None, None, "non-string published port entry")
    raw = value.strip()
    if "${" in raw or "$" in raw:
        return (None, None, "interpolated or dynamic short port mapping")
    if "/" in raw:
        raw, proto = raw.rsplit("/", 1)
        if proto.lower() not in ("tcp", "udp", "sctp"):
            return (None, None, "unrecognized protocol")
    if raw.startswith("["):
        m = re.fullmatch(r"(\[[^\]]+\]):(\d+(?:-\d+)?):(\d+(?:-\d+)?)", raw)
        if not m:
            return (None, None, "unsupported bracketed IPv6 mapping")
        return m.group(1), m.group(3), None
    parts = raw.split(":")
    if len(parts) == 1:
        if not re.fullmatch(r"\d+(?:-\d+)?", parts[0]):
            return (None, None, "unsupported container-port-only syntax")
        return (None, parts[0], None)
    if len(parts) == 2:
        if not all(re.fullmatch(r"\d+(?:-\d+)?", p) for p in parts):
            return (None, None, "unsupported host:container mapping")
        return (None, parts[1], None)
    if len(parts) == 3:
        if not all(re.fullmatch(r"\d+(?:-\d+)?", p) for p in parts[1:]):
            return (None, None, "unsupported IP:host:container mapping")
        return (parts[0], parts[2], None)
    return (None, None, "ambiguous port mapping")


def audit_compose(doc):
    if not isinstance(doc, dict):
        raise ValueError("Compose document must be a mapping")
    services = doc.get("services", {})
    if not isinstance(services, dict):
        raise ValueError("services must be a mapping")
    report = []
    for service, definition in services.items():
        service = str(service)
        if not isinstance(definition, dict):
            report.append(finding("review", "SERVICE_UNKNOWN", service, 0,
                                  "Service definition is not a mapping"))
            continue
        ports = definition.get("ports", [])
        if ports is None:
            ports = []
        if not isinstance(ports, list):
            report.append(finding("review", "PORTS_INVALID", service, 0,
                                  "ports is not a list"))
            continue
        if definition.get("network_mode") == "host" and ports:
            report.append(finding("review", "HOST_NETWORK_PORTS", service, 0,
                                  "Host networking bypasses normal published-port mappings; inspect deployment"))
        elif definition.get("network_mode") == "host":
            report.append(finding("review", "HOST_NETWORK", service, 0,
                                  "Host networking shares host network; inspect listeners and deployment"))
        for index, item in enumerate(ports, 1):
            host_ip = None
            target = None
            err = None
            if isinstance(item, dict):
                host_ip = item.get("host_ip")
                target = item.get("target")
                if not target or isinstance(target, (dict, list, bool)):
                    err = "Long-form published port target is missing or unsupported"
                elif item.get("mode") not in (None, "host", "ingress"):
                    err = "Unsupported publishing mode"
            else:
                host_ip, target, err = parse_short(item)
            if err:
                report.append(finding("review", "PORT_SYNTAX_REVIEW", service, index, err))
                continue
            category = address_class(host_ip)
            target_label = str(target)
            if category == "unspecified":
                report.append(finding("review", "DEFAULT_HOST_BIND", service, index,
                                      f"Container port {target_label}: no host IP set; Docker default may bind all interfaces (daemon/network settings can override)"))
            elif category == "wildcard":
                report.append(finding("high", "WILDCARD_HOST_BIND", service, index,
                                      f"Container port {target_label}: explicit wildcard host binding"))
            elif category == "other":
                report.append(finding("review", "NON_LOOPBACK_BIND", service, index,
                                      f"Container port {target_label}: explicitly bound to a non-loopback interface"))
            elif category == "dynamic":
                report.append(finding("review", "DYNAMIC_HOST_BIND", service, index,
                                      f"Container port {target_label}: host address cannot be resolved offline"))
    return sorted(report, key=lambda f: (f["service"], f["entry"], f["code"]))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("compose_file", type=Path, help="Local Compose YAML file")
    p.add_argument("--format", choices=["json", "text"], default="text")
    p.add_argument("--strict", action="store_true", help="Exit 2 when findings are present")
    args = p.parse_args(argv)
    try:
        doc = yaml.safe_load(args.compose_file.read_text(encoding="utf-8"))
        results = audit_compose(doc)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps({"findings": results, "count": len(results)}, indent=2))
    else:
        if not results:
            print("No modeled host-port binding findings (not proof of isolation).")
        for f in results:
            print(f"{f['severity'].upper()} [{f['code']}] {f['service']} ports[{f['entry']}]: {f['message']}")
        print(f"Findings: {len(results)}")
    return 2 if args.strict and results else 0


if __name__ == "__main__":
    raise SystemExit(main())
