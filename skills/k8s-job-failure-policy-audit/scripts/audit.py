#!/usr/bin/env python3
"""Offline Kubernetes Job pod-failure and retry contract auditor."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any
import yaml

NAME = "k8s-job-failure-policy-audit"
ACTIONS = {"Count", "Ignore", "FailJob", "FailIndex"}

def finding(rule: str, severity: str, file: str, doc: int, message: str, subject: str = "") -> dict[str, Any]:
    item={"rule":rule,"severity":severity,"file":file,"document":doc,"message":message}
    if subject: item["subject"]=subject
    return item

def job_specs(obj: dict[str, Any]):
    kind=obj.get("kind"); spec=obj.get("spec") or {}
    if kind == "Job": yield spec
    elif kind == "CronJob": yield (spec.get("jobTemplate") or {}).get("spec") or {}
    elif kind in {"JobList","CronJobList","List"}:
        for item in obj.get("items") or []:
            if isinstance(item,dict): yield from job_specs(item)

def audit_documents(documents: list[Any], file: str="<memory>") -> list[dict[str, Any]]:
    out=[]
    for index,obj in enumerate(documents,1):
        if not isinstance(obj,dict): continue
        for spec in job_specs(obj):
            name=((obj.get("metadata") or {}).get("name") or "<unnamed>")
            template=((spec.get("template") or {}).get("spec") or {})
            restart=template.get("restartPolicy", "")
            containers=template.get("containers") or []
            init=template.get("initContainers") or []
            names={c.get("name") for c in containers+init if isinstance(c,dict) and isinstance(c.get("name"),str)}
            policy=spec.get("podFailurePolicy")
            per_index=spec.get("backoffLimitPerIndex")
            max_failed=spec.get("maxFailedIndexes")
            mode=spec.get("completionMode", "NonIndexed")
            if policy is not None:
                if restart != "Never":
                    out.append(finding("POD_FAILURE_POLICY_REQUIRES_NEVER", "ERROR", file,index,"podFailurePolicy requires the Job Pod template restartPolicy to be Never",name))
                replacement=spec.get("podReplacementPolicy")
                if replacement not in (None,"Failed"):
                    out.append(finding("POD_REPLACEMENT_POLICY_INCOMPATIBLE", "ERROR",file,index,"When podFailurePolicy is set, podReplacementPolicy must be Failed",name))
                rules=policy.get("rules") if isinstance(policy,dict) else None
                if not isinstance(rules,list) or not rules:
                    out.append(finding("POD_FAILURE_RULES_REQUIRED","ERROR",file,index,"podFailurePolicy.rules must be a non-empty list",name))
                else:
                    for ri,rule in enumerate(rules,1):
                        if not isinstance(rule,dict):
                            out.append(finding("POD_FAILURE_RULE_INVALID","ERROR",file,index,f"Rule {ri} must be a mapping",name)); continue
                        action=rule.get("action")
                        if action not in ACTIONS:
                            out.append(finding("POD_FAILURE_ACTION_INVALID","ERROR",file,index,f"Rule {ri} has unsupported action {action!r}",name))
                        if action == "FailIndex" and per_index is None:
                            out.append(finding("FAIL_INDEX_REQUIBES_PER_INDEX","ERROR",file,index,f"Rule {ri} uses FailIndex but backoffLimitPerIndex is not set",name))
                        has_exit="onExitCodes" in rule and rule.get("onExitCodes") is not None
                        has_conditions="onPodConditions" in rule and rule.get("onPodConditions") is not None
                        if has_exit == has_conditions:
                            out.append(finding("POD_FAILURE_RULE_MATCHER_INVALID","ERROR",file,index,f"Rule {ri} must define exactly one of onExitCodes or onPodConditions",name))
                        if has_exit:
                            matcher=rule.get("onExitCodes") or {}
                            operator=matcher.get("operator")
                            values=matcher.get("values")
                            if operator not in {"In","NotIn"}:
                                out.append(finding("EXIT_CODE_OPERATOR_INVALID","ERROR",file,index,f"Rule {ri} operator must be In or NotIn",name))
                            if not isinstance(values,list) or not values or any(type(v) is not int or v < 0 for v in values):
                                out.append(finding("EXIT_CODE_VALUES_INVALID","ERROR",file,index,f"Rule {ri} values must be a non-empty list of non-negative integers",name))
                            else:
                                if len(values)!=len(set(values)) or values!=sorted(values):
                                    out.append(finding("EXIT_CODE_VALUES_ORDER_INVALID","ERROR",file,index,f"Rule {ri} values must be ordered and contain no duplicates",name))
                                if operator=="In" and 0 in values:
                                    out.append(finding("EXIT_CODE_ZERO_IN_INVALID","ERROR",file,index,f"Rule {ri} cannot include exit code 0 with operator In",name))
                            container=matcher.get("containerName")
                            if container is not None and container not in names:
                                out.append(finding("EXIT_CODE_CONTAINER_UNKNOWN","ERROR",file,index,f"Rule {ri} refers to container {container!r}, not found in containers or initContainers",name))
                        if has_conditions:
                            conditions=rule.get("onPodConditions")
                            if not isinstance(conditions,list) or not conditions or any(not isinstance(c,dict) or not isinstance(c.get("type"),str) or not c.get("type") for c in conditions):
                                out.append(finding("POD_CONDITIONS_INVALID","ERROR",file,index,f"Rule {ri} onPodConditions must be a non-empty list of objects with a non-empty type",name))
            if per_index is not None:
                if type(per_index) is not int or per_index < 0:
                    out.append(finding("BACKOFF_PER_INDEX_INVALID","ERROR",file,index,"backoffLimitPerIndex must be a non-negative integer",name))
                if mode != "Indexed":
                    out.append(finding("BACKOFF_PER_INDEX_REQUIRES_INDEXED","ERROR",file,index,"backoffLimitPerIndex can only be set for completionMode Indexed",name))
                if restart != "Never":
                    out.append(finding("BACKOFF_PER_INDEX_REQUIRES_NEVER","ERROR",file,index,"backoffLimitPerIndex requires Pod restartPolicy Never",name))
                if "backoffLimit" not in spec:
                    out.append(finding("INDEXED_BACKOFF_DEFAULT","INFO",file,index,"With backoffLimitPerIndex set and backoffLimit omitted, Kubernetes defaults backoffLimit to 2147483647 rather than 6",name))
            if max_failed is not None:
                if per_index is None:
                    out.append(finding("MAX_FAILED_INDEXES_REQUIRES_PER_INDEX","ERROR",file,index,"maxFailedIndexes can only be specified when backoffLimitPerIndex is set",name))
                if type(max_failed) is not int or max_failed < 0:
                    out.append(finding("MAX_FAILED_INDEXES_INVALID","ERROR",file,index,"maxFailedIndexes must be a non-negative integer",name))
                completions=spec.get("completions")
                if type(max_failed) is int and type(completions) is int and max_failed > completions:
                    out.append(finding("MAX_FAILED_INDEXES_EXCEEDS_COMPLETIONS","ERROR",file,index,"maxFailedIndexes must not exceed completions",name))
            if "backoffLimit" in spec and (type(spec["backoffLimit"]) is not int or spec["backoffLimit"] < 0):
                out.append(finding("BACKOFF_LIMIT_INVALID","ERROR",file,index,"backoffLimit must be a non-negative integer",name))
            if spec.get("successPolicy") is not None and mode != "Indexed":
                out.append(finding("SUCCESS_POLICY_REQUIRES_INDEXED","ERROR",file,index,"successPolicy is supported only for Indexed Jobs",name))
    return out

def audit_file(path: Path):
    try: docs=list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except (OSError,UnicodeError,yaml.YAMLError) as exc:
        return [finding("INPUT_PARSE_ERROR","ERROR",str(path),0,f"Cannot safely parse YAML: {exc}")]
    return audit_documents(docs,str(path))

def collect(paths):
    out=[]
    for raw in paths:
        p=Path(raw)
        if p.is_dir(): out.extend(sorted(x for x in p.rglob("*") if x.suffix.lower() in {".yaml",".yml"}))
        else: out.append(p)
    return out

def main(argv=None):
    p=argparse.ArgumentParser(description="Offline Kubernetes Job and CronJob failure/retry contract audit")
    p.add_argument("paths",nargs="+",help="YAML files or directories")
    p.add_argument("--format",choices=("text","json"),default="text")
    p.add_argument("--fail-on",choices=("error","warning","never"),default="error")
    a=p.parse_args(argv); files=collect(a.paths)
    if not files: print("No YAML files found",file=sys.stderr); return 1
    findings=[f for path in files for f in audit_file(path)]
    if a.format=="json": print(json.dumps({"tool":NAME,"findings":findings},indent=2))
    else:
        for f in findings: print(f"{f['severity']}: {f['rule']}: {f['file']}#{f['document']}: {f['message']}")
        print(f"Reviewed {len(files)} file(s); {len(findings)} finding(s)")
    if a.fail_on=="never": return 0
    threshold={"error":{"ERROR"},"warning":{"ERROR","WARNING"}}[a.fail_on]
    return 2 if any(f["severity"] in threshold for f in findings) else 0

if __name__=="__main__": raise SystemExit(main())
