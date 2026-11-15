#!/usr/bin/env python3
"""Offline review of Argo Rollouts AnalysisTemplate metrics and references."""
import argparse
import json
import sys
from pathlib import Path

import yaml

MAX_FILES = 500
MAX_SIZE = 2 * 1024 * 1024


def obj(value):
    return value if isinstance(value, dict) else {}


def seq(value):
    return value if isinstance(value, list) else []


def identity(resource):
    meta = obj(resource.get("metadata"))
    return f'{resource.get("kind", "?")}/{meta.get("namespace") or "default"}/{meta.get("name") or "?"}'


def report(code, severity, file, resource, detail, remediation):
    return {"code": code, "severity": severity, "file": file,
            "resource": identity(resource), "message": detail, "remediation": remediation}


def load(path):
    root = Path(path)
    if not root.exists() or root.is_symlink():
        raise ValueError("path must be an existing non-symlink file or directory")
    if root.is_dir():
        files = sorted(p for p in root.rglob("*")
                       if p.is_file() and p.suffix.lower() in {".yml", ".yaml"})
    else:
        files = [root]
    if not files or len(files) > MAX_FILES:
        raise ValueError("provide 1 to 500 YAML files")
    documents = []
    for path in files:
        if path.is_symlink() or path.stat().st_size > MAX_SIZE:
            raise ValueError(f"refusing symlink or oversized YAML: {path}")
        try:
            with path.open(encoding="utf-8") as source:
                for n, data in enumerate(yaml.safe_load_all(source), 1):
                    if data is None:
                        continue
                    if not isinstance(data, dict):
                        raise ValueError(f"{path} document {n} must be an object")
                    documents.append((str(path), data))
        except (UnicodeError, yaml.YAMLError) as exc:
            raise ValueError(f"invalid YAML in {path}: {exc}") from exc
    return documents


def is_argo(r):
    return r.get("apiVersion") == "argoproj.io/v1alpha1"


def valid_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def audit_metric(file, resource, metric):
    findings = []
    m = obj(metric)
    name = m.get("name") or "unnamed"
    add = lambda code, severity, msg, advice: findings.append(
        report(code, severity, file, resource, f"Metric {name}: {msg}", advice))
    if not m.get("name"):
        add("AR009", "error", "metric has no name", "Give each metric a stable unique name.")
    provider = obj(m.get("provider"))
    if len(provider) != 1:
        add("AR004", "error", "metric provider is absent or not a single supported provider object",
            "Configure exactly one provider (e.g. prometheus, web, datadog).")
    success = m.get("successCondition")
    failure = m.get("failureCondition")
    if not (isinstance(success, str) and success.strip()) and not (
            isinstance(failure, str) and failure.strip()):
        add("AR001", "warning", "neither successCondition nor failureCondition is defined",
            "Set at least one condition or document intentionally inconclusive manual review.")
    limit = m.get("failureLimit", 0)
    consecutive = m.get("consecutiveSuccessLimit", 0)
    if not valid_integer(limit) or limit < -1 or not valid_integer(consecutive) or consecutive < 0:
        add("AR003", "error", "failureLimit or consecutiveSuccessLimit has invalid type/range",
            "Use integer failureLimit >= -1 and consecutiveSuccessLimit >= 0 (Argo >=1.8 for latter).")
    elif limit == -1 and consecutive == 0:
        add("AR002", "error", "failureLimit disabled and consecutiveSuccessLimit disabled",
            "Enable failureLimit >= 0 or consecutiveSuccessLimit >= 1.")
    count = m.get("count")
    if count is not None and (not valid_integer(count) or count < 0):
        add("AR005", "error", "count must be a non-negative integer when specified",
            "Use count >= 0; count=0 has different behavior for inline vs background analysis.")
    for key in ("successCondition", "failureCondition"):
        if key in m and (not isinstance(m[key], str) or not m[key].strip()):
            add("AR010", "warning", f"{key} is blank or not a CEL expression string",
                "Supply a nonempty, reviewable CEL expression.")
    return findings


def rollout_analyses(rollout):
    strategy = obj(obj(rollout.get("spec")).get("strategy"))
    canary = obj(strategy.get("canary"))
    if canary:
        analysis = obj(canary.get("analysis"))
        if analysis:
            yield analysis
        for step in seq(canary.get("steps")):
            step_analysis = obj(obj(step).get("analysis"))
            if step_analysis:
                yield step_analysis
    blue = obj(strategy.get("blueGreen"))
    if blue:
        for key in ("prePromotionAnalysis", "postPromotionAnalysis"):
            analysis = obj(blue.get(key))
            if analysis:
                yield analysis


def audit(documents):
    findings = []
    templates = {}
    for file, resource in documents:
        if not is_argo(resource):
            continue
        kind = resource.get("kind")
        if kind not in {"AnalysisTemplate", "ClusterAnalysisTemplate"}:
            continue
        meta = obj(resource.get("metadata"))
        key = (kind, "GLOBAL" if kind == "ClusterAnalysisTemplate" else meta.get("namespace") or "default",
               meta.get("name"))
        if key in templates:
            findings.append(report("AR011", "error", file, resource,
                                   "duplicate template identity in input",
                                   "Give templates unique name/namespace/kind in the rendered set."))
        templates[key] = resource
        seen = set()
        for metric in seq(obj(resource.get("spec")).get("metrics")):
            name = obj(metric).get("name")
            if name in seen:
                findings.append(report("AR006", "error", file, resource,
                                       f"duplicate metric name {name}",
                                       "Use unique metric names within a template."))
            seen.add(name)
            findings.extend(audit_metric(file, resource, metric))
        if not seq(obj(resource.get("spec")).get("metrics")):
            findings.append(report("AR012", "warning", file, resource, "template contains no metrics",
                                   "Verify whether this empty template is intentional."))
    for file, resource in documents:
        if not is_argo(resource) or resource.get("kind") != "Rollout":
            continue
        namespace = obj(resource.get("metadata")).get("namespace") or "default"
        canary = obj(obj(obj(resource.get("spec")).get("strategy")).get("canary"))
        start = obj(canary.get("analysis")).get("startingStep")
        steps = seq(canary.get("steps"))
        if start is not None and (not valid_integer(start) or start < 0 or start >= len(steps)):
            findings.append(report("AR013", "warning", file, resource,
                                   "canary analysis startingStep is outside declared steps",
                                   "Choose a zero-based startingStep within canary steps."))
        for analysis in rollout_analyses(resource):
            args = {obj(a).get("name") for a in seq(analysis.get("args"))}
            for entry in seq(analysis.get("templates")):
                ref = obj(entry)
                name = ref.get("templateName")
                if not isinstance(name, str) or not name:
                    findings.append(report("AR014", "error", file, resource, "analysis template reference has no templateName",
                                           "Provide the AnalysisTemplate/ClusterAnalysisTemplate name."))
                    continue
                scope = bool(ref.get("clusterScope", False))
                kind = "ClusterAnalysisTemplate" if scope else "AnalysisTemplate"
                key = (kind, "GLOBAL" if scope else namespace, name)
                if key not in templates:
                    findings.append(report("AR007", "warning", file, resource,
                                           f"{kind}/{name} not present in provided YAML",
                                           "Include the template in the review bundle or verify it exists in the cluster."))
                    continue
                definition = templates[key]
                required = [obj(a).get("name") for a in seq(obj(definition.get("spec")).get("args"))
                            if obj(a).get("name") and "value" not in obj(a)]
                missing = sorted(set(required) - args)
                if missing:
                    findings.append(report("AR008", "warning", file, resource,
                                           f"{kind}/{name} is missing required args: {', '.join(missing)}",
                                           "Supply required analysis args or add documented defaults."))
    return sorted(findings, key=lambda x: (x["file"], x["resource"], x["code"], x["message"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="YAML file or directory containing rendered Argo Rollouts")
    parser.add_argument("--json", action="store_true")
    options = parser.parse_args(argv)
    try:
        findings = audit(load(options.path))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}) if options.json else f"Input error: {exc}", file=sys.stderr)
        return 2
    if options.json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        for item in findings:
            print(f'{item["code"]} [{item["severity"]}] {item["resource"]}: {item["message"]}')
        print(f"Review findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
