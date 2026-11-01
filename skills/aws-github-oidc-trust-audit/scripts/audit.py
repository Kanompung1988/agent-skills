#!/usr/bin/env python3
"""Offline, conservative GitHub OIDC IAM role trust-policy review (stdlib only)."""
import argparse
import json
import sys
from pathlib import Path

SUB = "token.actions.githubusercontent.com:sub"
AUD = "token.actions.githubusercontent.com:aud"
PROVIDER = "oidc-provider/token.actions.githubusercontent.com"
ACTION = "sts:AssumeRoleWithWebIdentity"
MAX_BYTES = 2_000_000

class InputError(Exception):
    pass

def _unique_pairs(pairs):
    result = {}
    for key, val in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = val
    return result

def _items(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]

def _strings(value):
    return [str(item) for item in _items(value) if isinstance(item, str)]

def _finding(code, severity, file_name, statement, detail):
    return {"code": code, "severity": severity, "file": file_name,
            "statement": statement, "detail": detail}

def _policy(payload):
    if not isinstance(payload, dict):
        raise InputError("policy must be a JSON object")
    if "AssumeRolePolicyDocument" in payload:
        payload = payload["AssumeRolePolicyDocument"]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload, object_pairs_hook=_unique_pairs)
            except (ValueError, TypeError) as exc:
                raise InputError("invalid embedded policy JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("Statement"), (dict, list)):
        raise InputError("expected IAM policy Statement object or array")
    statements = _items(payload["Statement"])
    if not all(isinstance(statement, dict) for statement in statements):
        raise InputError("Statement must contain only JSON objects")
    return statements

def _github_provider(principal):
    if not isinstance(principal, dict):
        return False
    return any(value.endswith(PROVIDER) for value in _strings(principal.get("Federated")))

def _subject_scope(value):
    if value == "*":
        return "broad"
    if not value.startswith("repo:"):
        return "unknown"
    rest = value[5:]
    if ":" not in rest:
        return "broad"
    repository, qualifier = rest.split(":", 1)
    if not repository or "/" not in repository:
        return "unknown"
    owner, name = repository.split("/", 1)
    if not owner or not name or any(char in owner + name for char in "*?"):
        return "broad"
    if any(char in qualifier for char in "*?"):
        return "wildcard-ref"
    if qualifier.startswith(("ref:refs/heads/", "ref:refs/tags/", "environment:", "pull_request")):
        return "exact"
    return "unknown"

def inspect_policy(payload, file_name):
    statements = _policy(payload)
    findings, matched = [], 0
    for index, statement in enumerate(statements):
        if statement.get("Effect") != "Allow" or not _github_provider(statement.get("Principal")):
            continue
        actions = {name.lower() for name in _strings(statement.get("Action"))}
        if ACTION.lower() not in actions and "*" not in actions and "sts:*" not in actions:
            continue
        matched += 1
        condition = statement.get("Condition", {})
        if not isinstance(condition, dict):
            findings.append(_finding("INVALID_CONDITION", "HIGH", file_name, index,
                                     "Condition is not an object; manual review required."))
            continue
        subs, audiences, unsupported = [], [], False
        for op, values in condition.items():
            if not isinstance(values, dict):
                unsupported = True
                continue
            if op in ("StringEquals", "StringLike"):
                subs.extend(_strings(values.get(SUB)))
                audiences.extend(_strings(values.get(AUD)))
            elif SUB in values or AUD in values:
                unsupported = True
        if unsupported:
            findings.append(_finding("UNSUPPORTED_OPERATOR", "REVIEW", file_name, index,
                                     "Conditions use operators or shapes outside this static model."))
        if not subs:
            findings.append(_finding("MISSING_POSITIVE_SUB", "HIGH", file_name, index,
                                     "No supported positive GitHub subject restriction was found."))
        else:
            scopes = [_subject_scope(s) for s in subs]
            if "broad" in scopes:
                findings.append(_finding("BROAD_REPOSITORY_SUB", "HIGH", file_name, index,
                                         "At least one allowed subject can match multiple repositories."))
            if "wildcard-ref" in scopes:
                findings.append(_finding("WILDCARD_REF_SUB", "REVIEW", file_name, index,
                                         "At least one allowed subject uses a wildcard in its ref or context."))
            if "unknown" in scopes:
                findings.append(_finding("UNRECOGNIZED_SUB", "REVIEW", file_name, index,
                                         "At least one subject is outside the recognized exact GitHub formats."))
            if any(":environment:" in s for s in subs):
                findings.append(_finding("ENVIRONMENT_GATES", "REVIEW", file_name, index,
                                         "An environment subject requires checking GitHub environment protection."))
        if not audiences:
            findings.append(_finding("MISSING_POSITIVE_AUD", "HIGH", file_name, index,
                                     "No supported positive GitHub audience restriction was found."))
        elif "sts.amazonaws.com" not in audiences:
            findings.append(_finding("NONSTANDARD_AUDIENCE", "REVIEW", file_name, index,
                                     "Audience is not sts.amazonaws.com; verify intended AWS setup."))
        elif any(a != "sts.amazonaws.com" for a in audiences):
            findings.append(_finding("MULTIPLE_AUDIENCES", "REVIEW", file_name, index,
                                     "Audience restriction also accepts an additional value."))
        if "*" in actions or "sts:*" in actions:
            findings.append(_finding("WILDCARD_ACTION", "REVIEW", file_name, index,
                                     "Trust statement accepts an unrestricted action name."))
    return findings, matched

def audit(path):
    root = Path(path)
    if root.is_symlink():
        raise InputError("symlink input refused")
    if not root.exists():
        raise InputError("input path does not exist")
    paths = sorted(root.rglob("*.json")) if root.is_dir() else [root]
    if len(paths) > 100:
        raise InputError("too many JSON files (limit 100)")
    if not paths:
        raise InputError("no JSON files found")
    findings, files, count = [], [], 0
    for file in paths:
        if file.is_symlink() or not file.is_file():
            raise InputError("symlink or non-file input refused")
        if file.stat().st_size > MAX_BYTES:
            raise InputError("input exceeds 2 MB limit")
        name = str(file.relative_to(root)) if root.is_dir() else file.name
        try:
            payload = json.loads(file.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
        except (UnicodeError, ValueError, OSError) as exc:
            raise InputError("invalid JSON input: " + name) from exc
        current, matches = inspect_policy(payload, name)
        count += matches
        files.append(name)
        findings.extend(current)
    findings.sort(key=lambda f: (f["file"], f["statement"], f["code"]))
    return {"files": files, "github_allow_statements": count, "findings": findings,
            "summary": {"HIGH": sum(x["severity"] == "HIGH" for x in findings),
                        "REVIEW": sum(x["severity"] == "REVIEW" for x in findings)}}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="IAM trust policy JSON file or directory")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("high", "review", "never"), default="high")
    args = parser.parse_args(argv)
    try:
        result = audit(args.path)
    except (InputError, OSError) as exc:
        print("INPUT_ERROR: " + str(exc), file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Reviewed %s file(s); %s matching GitHub OIDC allow statement(s)." %
              (len(result["files"]), result["github_allow_statements"]))
        for item in result["findings"]:
            print("%s %s %s statement[%s]: %s" %
                  (item["severity"], item["code"], item["file"],
                   item["statement"], item["detail"]))
        if not result["findings"]:
            print("No modelled findings; this is not an authorization proof.")
    if args.fail_on == "never":
        return 0
    if args.fail_on == "high":
        return int(result["summary"]["HIGH"] > 0)
    return int(bool(result["findings"]))

if __name__ == "__main__":
    sys.exit(main())
