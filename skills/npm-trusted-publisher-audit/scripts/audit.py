#!/usr/bin/env python3
"""Offline, read-only npm trusted-publisher release workflow reviewer."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml

PUBLISH = re.compile(r"\bnpm\s+(?:stage\s+)?publish\b")
GH_REPO = re.compile(r"github\.com[:/]([^/\s]+/[^/\s#]+)", re.I)
LIMIT = 1024 * 1024

class InputError(ValueError):
    pass

def read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > LIMIT:
        raise InputError("file absent, symlinked, or larger than 1 MiB: " + path.name)
    return path.read_text(encoding="utf-8")

def obj(value):
    return value if isinstance(value, dict) else {}

def disabled(value):
    return str(value).lower() == "false"

def triggers(value):
    if isinstance(value, dict): return set(value.keys())
    if isinstance(value, list): return set(str(x) for x in value)
    return {str(value)}

def token_key(value):
    if isinstance(value, dict): return any(token_key(k) or token_key(v) for k,v in value.items())
    if isinstance(value, list): return any(token_key(v) for v in value)
    return bool(re.search(r"\b(NPM_TOKEN|NODE_AUTH_TOKEN|NPM_AUTH_TOKEN)\b", str(value), re.I))

def github_repo(value):
    if isinstance(value, dict): value=value.get("url", "")
    if not isinstance(value, str): return ""
    match=GH_REPO.search(value)
    return match.group(1).removesuffix(".git").strip("/") if match else ""

def analyze(root):
    root=Path(root)
    if root.is_symlink() or not root.is_dir():
        raise InputError("project root must be an existing non-symlink directory")
    package=json.loads(read(root/"package.json"))
    if not isinstance(package,dict): raise InputError("package.json must be a JSON object")
    folder=root/".github"/"workflows"
    if folder.is_symlink() or not folder.is_dir():
        raise InputError("missing .github/workflows directory")
    paths=sorted(set(folder.glob("*.yml"))|set(folder.glob("*.yaml")))
    if not paths: raise InputError("no YAML workflows found")
    inventory_file=root/"trusted-publisher.json"
    inventory=None
    if inventory_file.exists() or inventory_file.is_symlink():
        inventory=json.loads(read(inventory_file))
        if not isinstance(inventory,dict): raise InputError("inventory must be JSON object")
    findings=[]
    def add(rule,severity,file,job,detail):
        findings.append(dict(rule=rule,severity=severity,file=file,job=job,detail=detail))
    if inventory is not None:
        expected=inventory.get("repository","")
        wf=inventory.get("workflow","")
        if not isinstance(expected,str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", expected):
            raise InputError("inventory repository must be owner/repo")
        if not isinstance(wf,str) or not wf.endswith((".yml",".yaml")):
            raise InputError("inventory workflow must be YAML filename")
        if github_repo(package.get("repository")) != expected:
            add("NPM_REPOSITORY_MISMATCH","high","package.json","",
                "package repository does not match the declared publisher repository")
    if disabled(obj(package.get("publishConfig")).get("provenance","true")):
        add("NPM_PROVENANCE_DISABLED","high","package.json","",
            "package publishConfig disables provenance")
    published=[]
    for path in paths:
        config=yaml.load(read(path), Loader=yaml.BaseLoader)
        if not isinstance(config,dict): raise InputError("workflow must be YAML mapping: "+path.name)
        events=triggers(config.get("on",{}))
        jobs=obj(config.get("jobs"))
        for job_name,raw in jobs.items():
            job=obj(raw)
            steps=job.get("steps",[])
            if not isinstance(steps,list): raise InputError("job steps not a list: "+path.name)
            commands=[obj(s) for s in steps if PUBLISH.search(str(obj(s).get("run","")))]
            if not commands: continue
            published.append(path.name)
            scope=job.get("permissions",config.get("permissions"))
            if obj(scope).get("id-token") != "write":
                add("NPM_ID_TOKEN_MISSING","high",path.name,str(job_name),
                    "publishing job lacks effective explicit id-token: write")
            runner=str(job.get("runs-on","")).lower()
            if "self-hosted" in runner:
                add("NPM_UNSUPPORTED_RUNNER","high",path.name,str(job_name),
                    "publish job selects self-hosted runner")
            elif "$" in runner or not runner:
                add("NPM_RUNNER_DYNAMIC","review",path.name,str(job_name),
                    "runner eligibility requires manual evaluation")
            if events.intersection({"pull_request","pull_request_target"}):
                add("NPM_PR_PUBLISH_TRIGGER","high",path.name,str(job_name),
                    "PR event can trigger workflow; inspect conditions")
            if "workflow_call" in events:
                add("NPM_CALLER_IDENTITY","review",path.name,str(job_name),
                    "reusable publish requires checking the calling workflow identity")
            if token_key(config.get("env")) or token_key(job.get("env")) or any(
                token_key(step.get("env")) for step in commands):
                add("NPM_TOKEN_FALLBACK","review",path.name,str(job_name),
                    "publish job declares token-related environment keys")
            for step in commands:
                command=str(step.get("run",""))
                if re.search(r"--provenance(?:=|\s+)false\b",command,re.I) or disabled(
                    obj(step.get("env")).get("NPM_CONFIG_PROVENANCE","true")):
                    add("NPM_PROVENANCE_DISABLED","high",path.name,str(job_name),
                        "publish step explicitly disables provenance")
    if not published:
        add("NPM_NO_PUBLISH_JOB","review",".github/workflows","",
            "no directly recognized npm publish command; wrapper actions are out of scope")
    if inventory is None:
        add("NPM_PUBLISHER_UNVERIFIED","review","trusted-publisher.json","",
            "no declared publisher inventory; npm registry config is unverified")
    elif inventory["workflow"] not in published:
        add("NPM_WORKFLOW_MISMATCH","high","trusted-publisher.json","",
            "declared publisher workflow has no directly recognized npm publish")
    return {"count":len(findings),"findings":findings,
            "note":"offline heuristics; inventory is not proof of npm registry configuration"}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args(argv)
    try:
        result=analyze(args.project)
    except (OSError,UnicodeError,ValueError,json.JSONDecodeError,yaml.YAMLError) as exc:
        print("INPUT ERROR: "+str(exc),file=sys.stderr)
        return 2
    if args.json: print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print(str(result["count"])+" review finding(s)")
        for f in result["findings"]: print(f["severity"]+": "+f["rule"]+" ("+f["file"]+")")
    return 1 if result["count"] else 0

if __name__=="__main__":
    sys.exit(main())
