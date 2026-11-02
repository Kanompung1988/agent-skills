#!/usr/bin/env python3
"""Offline, read-only Docker Compose startup dependency/readiness diagnostics."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

CONDITIONS = {"service_started", "service_healthy", "service_completed_successfully"}
RESTARTS = {"always", "unless-stopped"}
MAX_BYTES = 2_000_000


def finding(code: str, severity: str, service: str, detail: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "service": service, "detail": detail}


def check(data: Any) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(data, dict) or not isinstance(data.get("services"), dict):
        return [finding("INVALID_SERVICES", "error", "-", "Compose document must contain a services mapping")]
    services = data["services"]
    edges: dict[str, set[str]] = {str(k): set() for k in services}
    for name, definition in sorted(services.items(), key=lambda x: str(x[0])):
        if not isinstance(name, str) or not isinstance(definition, dict):
            issues.append(finding("INVALID_SERVICE", "error", str(name), "Service definition must be a mapping"))
            continue
        health = definition.get("healthcheck")
        if health is not None:
            if not isinstance(health, dict):
                issues.append(finding("INVALID_HEALTHCHECK", "error", name, "healthcheck must be a mapping"))
            else:
                test = health.get("test")
                if test is not None and (not isinstance(test, (str, list)) or isinstance(test, list) and (not test or not all(isinstance(v, str) for v in test))):
                    issues.append(finding("INVALID_HEALTHCHECK_TEST", "error", name, "healthcheck.test must be a string or nonempty string array"))
                for field in ("interval", "timeout", "start_period", "start_interval"):
                    v = health.get(field)
                    if v is not None and (not isinstance(v, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?(?:ns|us|ms|s|m|h)(?:[0-9]+(?:\.[0-9]+)?(?:ns|us|ms|s|m|h))*", v)):
                        issues.append(finding("INVALID_HEALTH_DURATION", "review", name, f"Check healthcheck.{field} duration syntax"))
                retries = health.get("retries")
                if retries is not None and (not isinstance(retries, int) or isinstance(retries, bool) or retries < 1):
                    issues.append(finding("INVALID_RETRIES", "error", name, "healthcheck.retries must be a positive integer"))
        dependencies = definition.get("depends_on", {})
        if isinstance(dependencies, list):
            dependencies = {x: {"condition": "service_started"} for x in dependencies if isinstance(x, str)}
            if len(dependencies) != len(definition["depends_on"]):
                issues.append(finding("INVALID_DEPENDENCY", "error", name, "depends_on list must contain service names"))
        elif dependencies is None:
            dependencies = {}
        elif not isinstance(dependencies, dict):
            issues.append(finding("INVALID_DEPENDS_ON", "error", name, "depends_on must be a list or mapping"))
            continue
        for dep, settings in sorted(dependencies.items(), key=lambda x: str(x[0])):
            if not isinstance(dep, str):
                issues.append(finding("INVALID_DEPENDENCY", "error", name, "Dependency names must be strings"))
                continue
            if not isinstance(settings, dict):
                issues.append(finding("INVALID_DEPENDENCY", "error", name, f"{dep}: dependency configuration must be mapping"))
                continue
            condition = settings.get("condition", "service_started")
            if condition not in CONDITIONS:
                issues.append(finding("UNKNOWN_CONDITION", "error", name, f"{dep}: unsupported condition {condition!r}"))
            if settings.get("required", True) is False:
                issues.append(finding("OPTIONAL_DEPENDENCY", "review", name, f"{dep}: required=false; dependent may start without it"))
            if dep not in services:
                issues.append(finding("MISSING_SERVICE", "error", name, f"{dep}: dependency is not in this Compose document"))
                continue
            edges[name].add(dep)
            target = services[dep]
            if not isinstance(target, dict):
                continue
            if condition == "service_healthy":
                h = target.get("healthcheck")
                if not isinstance(h, dict) or not h.get("test") or h.get("disable") is True or h.get("test") in (["NONE"], "NONE"):
                    issues.append(finding("MISSING_HEALTHCHECK", "error", name, f"{dep}: service_healthy requires an enabled healthcheck"))
            elif condition == "service_started":
                issues.append(finding("STARTED_NOT_READY", "review", name, f"{dep}: service_started checks startup order, not application readiness"))
            if condition == "service_completed_successfully" and str(target.get("restart", "")).lower() in RESTARTS:
                issues.append(finding("CONFLICTING_RESTART", "review", name, f"{dep}: completion dependency has a continuously restarting policy"))
    state: dict[str, int] = {}
    recorded: set[tuple[str, ...]] = set()
    def visit(node: str, path: list[str]) -> None:
        state[node] = 1
        for dep in sorted(edges[node]):
            if state.get(dep) == 1:
                idx = path.index(dep) if dep in path else 0
                cycle = tuple(path[idx:] + [dep])
                if cycle not in recorded:
                    recorded.add(cycle)
                    issues.append(finding("DEPENDENCY_CYCLE", "error", node, " -> ".join(cycle)))
            elif state.get(dep, 0) == 0:
                visit(dep, path + [dep])
        state[node] = 2
    for service in sorted(edges):
        if state.get(service, 0) == 0:
            visit(service, [service])
    return sorted(issues, key=lambda i: (i["service"], i["code"], i["detail"]))


def audit(path: Path) -> list[dict[str, str]]:
    if yaml is None:
        raise RuntimeError("PyYAML is required: pip install PyYAML>=6,<7")
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Input must be a file <= 2MB")
    raw = path.read_text(encoding="utf-8")
    docs = list(yaml.safe_load_all(raw))
    if len(docs) != 1:
        raise ValueError("Expected exactly one Compose YAML document")
    return check(docs[0])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compose", type=Path, help="Local Docker Compose YAML file")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 on error-severity findings")
    args = parser.parse_args(argv)
    try:
        results = audit(args.compose)
    except (OSError, UnicodeError, ValueError, RuntimeError, yaml.YAMLError if yaml else ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"findings": results, "count": len(results)}, indent=2))
    else:
        for item in results:
            print(f"{item['severity'].upper():6} {item['code']}: {item['service']} — {item['detail']}")
        print(f"{len(results)} finding(s)")
    return 1 if args.strict and any(x["severity"] == "error" for x in results) else 0


if __name__ == "__main__":
    sys.exit(main())
