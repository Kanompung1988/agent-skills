#!/usr/bin/env python3
"""Offline Argo CD sync-option contract reviewer."""
import argparse
import json
import sys
from pathlib import Path
import yaml

def finding(code, message, scope):
    return {"code":code,"message":message,"resource":scope}

def options_from_list(value, scope, out):
    parsed={}
    if value is None:
        return parsed
    if not isinstance(value, list):
        out.append(finding("AO001", "syncOptions must be a list of Key=value strings.", scope))
        return parsed
    for opt in value:
        if not isinstance(opt, str) or "=" not in opt:
            out.append(finding("AO001", "Invalid sync option; expected Key=value string.", scope))
            continue
        name, val = (s.strip() for s in opt.split("=",1))
        if not name or not val:
            out.append(finding("AO001", "Empty sync option key/value.", scope))
            continue
        if name in parsed and parsed[name] != val:
            out.append(finding("AO002", "Contradictory values for " + name + ".", scope))
        parsed[name]=val
    return parsed

def report_opts(opts, scope, out):
    if opts.get("Replace") == "true":
        out.append(finding("AO003", "Replace=true can recreate resources; review impact.", scope))
        if opts.get("ServerSideApply") == "true":
            out.append(finding("AO004", "Replace=true takes precedence over ServerSideApply=true.", scope))
    if opts.get("Force") == "true":
        out.append(finding("AO005", "Force=true may delete/recreate resources depending on apply mode.", scope))
    if opts.get("Validate") == "false":
        out.append(finding("AO006", "Validate=false disables Kubernetes schema validation during sync.", scope))
    if opts.get("SkipDryRunOnMissingResource") == "true":
        out.append(finding("AO007", "SkipDryRunOnMissingResource=true skips a validation safeguard.", scope))
    if opts.get("Prune") == "false":
        out.append(finding("AO008", "Prune=false retains resources after removal from Git; review drift policy.", scope))
    if opts.get("Force") == "true" and opts.get("ServerSideApply") == "true" and opts.get("Replace") != "true":
        out.append(finding("AO009", "Force=true alone is ignored in server-side apply; check intended behavior.", scope))

def review(doc):
    if not isinstance(doc, dict):
        return []
    meta = doc.get("metadata") or {}
    if not isinstance(meta, dict):
        raise ValueError("metadata must be mapping")
    scope = str(doc.get("kind","Unknown")) + "/" + str(meta.get("name","<unnamed>"))
    findings=[]
    if doc.get("kind") == "Application" and str(doc.get("apiVersion","")).startswith("argoproj.io/"):
        spec=doc.get("spec") or {}
        if not isinstance(spec,dict): raise ValueError("spec must be mapping")
        policy=spec.get("syncPolicy") or {}
        if not isinstance(policy,dict): raise ValueError("syncPolicy must be mapping")
        opts=options_from_list(policy.get("syncOptions"),scope,findings)
        report_opts(opts,scope,findings)
        automated=policy.get("automated") or {}
        if isinstance(automated,dict) and automated.get("prune") is True and automated.get("allowEmpty") is True:
            findings.append(finding("AO010","Automated prune+allowEmpty can remove all managed resources when source is empty.",scope))
        if spec.get("ignoreDifferences") and opts.get("RespectIgnoreDifferences") != "true":
            findings.append(finding("AO011","ignoreDifferences exists without RespectIgnoreDifferences=true; sync may still apply ignored fields.",scope))
    annotations=meta.get("annotations") or {}
    if not isinstance(annotations,dict): raise ValueError("annotations must be mapping")
    raw=annotations.get("argocd.argoproj.io/sync-options")
    if raw is not None:
        if not isinstance(raw,str):
            findings.append(finding("AO001","Sync-options annotation must be a comma-separated string.",scope))
        else:
            opts=options_from_list([item.strip() for item in raw.split(",")],scope,findings)
            report_opts(opts,scope,findings)
    return findings

def collect(path):
    if path.is_symlink(): raise ValueError("Refusing symlink input")
    if path.is_file(): return [path]
    if not path.is_dir(): raise ValueError("Path does not exist")
    return sorted(x for x in path.rglob("*") if x.is_file() and not x.is_symlink() and x.suffix.lower() in (".yml",".yaml"))

def analyze(path):
    findings=[]
    count=0
    for f in collect(Path(path)):
        if f.stat().st_size > 2 * 1024 * 1024: raise ValueError("YAML exceeds 2 MiB: " + str(f))
        try: docs=list(yaml.safe_load_all(f.read_text(encoding="utf-8")))
        except (yaml.YAMLError,OSError,UnicodeError) as e: raise ValueError("Cannot parse " + str(f) + ": " + str(e)) from e
        for index, doc in enumerate(docs,1):
            count+=1
            for row in review(doc):
                findings.append({"file":str(f),"document":index,**row})
    return {"documents_scanned":count,"findings":findings}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("path")
    p.add_argument("--json",action="store_true")
    args=p.parse_args(argv)
    try: result=analyze(args.path)
    except (ValueError,OSError) as e:
        print("ERROR: "+str(e),file=sys.stderr)
        return 2
    if args.json: print(json.dumps(result,sort_keys=True,indent=2))
    else:
        for f in result["findings"]:
            print(f'{f["file"]}:{f["document"]} {f["code"]}: {f["message"]}')
        print(f'{result["documents_scanned"]} documents, {len(result["findings"])} findings')
    return 1 if result["findings"] else 0

if __name__=="__main__": sys.exit(main())
