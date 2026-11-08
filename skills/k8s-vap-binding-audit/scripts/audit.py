#!/usr/bin/env python3
"""Offline ValidatingAdmissionPolicy/Binding relationship review."""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: python -m pip install 'PyYAML>=6,<7'")

MAX_FILES = 100
MAX_BYTES = 1024 * 1024
TARGET = {"ValidatingAdmissionPolicy", "ValidatingAdmissionPolicyBinding"}
GROUP = "admissionregistration.k8s.io/v1"


def finding(rule, kind, name, message):
    return {"rule":rule,"kind":kind,"object":name,"message":message}


def audit_objects(objects):
    findings = []
    policies, bindings = {}, []
    for doc in objects:
        if not isinstance(doc, dict) or doc.get("kind") not in TARGET:
            continue
        kind = doc.get("kind")
        if doc.get("apiVersion") != GROUP:
            findings.append(finding("VP001",kind,str(doc.get("metadata",{}).get("name","<unknown>")),
                                    "Only admissionregistration.k8s.io/v1 is supported; review version manually"))
            continue
        meta = doc.get("metadata") or {}
        spec = doc.get("spec") or {}
        if not isinstance(meta,dict) or not isinstance(spec,dict):
            raise ValueError("policy metadata/spec must be mappings")
        name = meta.get("name")
        if not isinstance(name,str) or not name:
            raise ValueError("VAP and binding objects require metadata.name")
        if kind == "ValidatingAdmissionPolicy":
            if name in policies:
                findings.append(finding("VP002",kind,name,"duplicate local policy name"))
            policies[name] = spec
        else:
            bindings.append((name,spec))
    linked = set()
    for name,spec in bindings:
        kind = "ValidatingAdmissionPolicyBinding"
        policy_name = spec.get("policyName")
        if not isinstance(policy_name,str) or not policy_name:
            findings.append(finding("VP003",kind,name,"policyName missing"))
            continue
        policy = policies.get(policy_name)
        if policy is None:
            findings.append(finding("VP004",kind,name,
                                    "referenced policy not in supplied bundle; it might exist in cluster"))
        else:
            linked.add(policy_name)
        actions = spec.get("validationActions")
        if not isinstance(actions,list) or not actions:
            findings.append(finding("VP005",kind,name,"validationActions missing or empty"))
            actions = []
        if any(a not in ("Deny","Warn","Audit") for a in actions):
            findings.append(finding("VP005",kind,name,"validationActions has an unknown value"))
        if "Deny" in actions and "Warn" in actions:
            findings.append(finding("VP006",kind,name,"Deny and Warn cannot be combined"))
        if actions and "Deny" not in actions:
            findings.append(finding("VP007",kind,name,
                                    "non-denying Warn/Audit binding; intentional monitoring or enforcement gap?"))
        ref = spec.get("paramRef")
        if policy is not None:
            has_kind = bool(policy.get("paramKind"))
            if has_kind and not isinstance(ref,dict):
                findings.append(finding("VP008",kind,name,
                                        "policy has paramKind but binding has no paramRef; review parameter use"))
            if not has_kind and isinstance(ref,dict):
                findings.append(finding("VP008",kind,name,
                                        "binding paramRef is ignored when policy has no paramKind"))
        if ref is not None:
            if not isinstance(ref,dict):
                raise ValueError("paramRef must be a mapping")
            has_name,has_selector = bool(ref.get("name")), "selector" in ref
            if has_name == has_selector:
                findings.append(finding("VP009",kind,name,
                                        "paramRef must specify exactly one of name or selector"))
            if ref.get("parameterNotFoundAction") not in ("Allow","Deny"):
                findings.append(finding("VP010",kind,name,
                                        "parameterNotFoundAction is required (Allow or Deny)"))
            elif ref["parameterNotFoundAction"] == "Allow":
                findings.append(finding("VP011",kind,name,
                                        "missing parameter is treated as successful validation"))
    for name,spec in policies.items():
        if name not in linked:
            findings.append(finding("VP012","ValidatingAdmissionPolicy",name,
                                    "no binding in supplied bundle; policy may be bound elsewhere"))
        if spec.get("failurePolicy") == "Ignore":
            findings.append(finding("VP013","ValidatingAdmissionPolicy",name,
                                    "failurePolicy Ignore skips evaluation errors; review fail-open intent"))
        constraints = spec.get("matchConstraints")
        if isinstance(constraints,dict) and not constraints.get("resourceRules"):
            findings.append(finding("VP014","ValidatingAdmissionPolicy",name,
                                    "matchConstraints has no resourceRules; check API validity/scope"))
    return sorted(findings,key=lambda x:(x["kind"],x["object"],x["rule"],x["message"]))


def audit_path(target):
    path = Path(target)
    if path.is_symlink():
        raise ValueError("symlink inputs are not followed")
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted([*path.glob("*.yaml"), *path.glob("*.yml")])
    else:
        raise ValueError("path does not exist")
    if not files or len(files) > MAX_FILES:
        raise ValueError("expected 1–100 YAML files")
    objects = []
    for path in files:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe or oversized input YAML")
        try:
            docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except (yaml.YAMLError,UnicodeError) as exc:
            raise ValueError("invalid YAML: "+path.name) from exc
        if len(docs)>200:
            raise ValueError("too many YAML documents")
        objects.extend(docs)
    findings = audit_objects(objects)
    return {"count":len(findings),"findings":findings}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path",help="rendered YAML file or YAML directory")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args(argv)
    try:
        result=audit_path(args.path)
    except (OSError,ValueError) as exc:
        print("ERROR: "+str(exc),file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result,sort_keys=True))
    else:
        print("Admission contract review findings:",result["count"])
        for f in result["findings"]:
            print("{kind}/{object}: {rule}: {message}".format(**f))
    return 1 if result["count"] else 0


if __name__=="__main__":
    sys.exit(main())
