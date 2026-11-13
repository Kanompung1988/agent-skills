#!/usr/bin/env python3
"""Read-only workflow cache-mode trust-boundary review."""
import argparse
import json
import sys
from pathlib import Path
import yaml

LIMIT=2*1024*1024
VALID={"read","write","write-only","none"}
LOW={"pull_request","pull_request_target","issue_comment","issues","discussion_comment","pull_request_review_comment","workflow_run","repository_dispatch"}

def paths(target):
    if target.is_symlink(): raise ValueError("symlink input not supported")
    if target.is_file(): return [target]
    if not target.is_dir(): raise ValueError("expected a YAML file or directory")
    return sorted(p for p in target.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in (".yaml",".yml"))

def finding(p,rule,level,job,msg):
    return {"path":str(p),"rule":rule,"severity":level,"location":"jobs."+str(job),"message":msg}

def events(value):
    if isinstance(value,str): return {value}
    if isinstance(value,list): return {str(x) for x in value}
    if isinstance(value,dict): return {str(x) for x in value}
    return set()

def inspect(doc,p):
    if not isinstance(doc,dict): raise ValueError("workflow root must be a mapping")
    jobs=doc.get("jobs",{})
    if not isinstance(jobs,dict): raise ValueError("jobs must be a mapping")
    risky=sorted(events(doc.get("on")) & LOW)
    out=[]
    for name,job in sorted(jobs.items(),key=lambda x:str(x[0])):
        if not isinstance(job,dict): continue
        explicit="cache-mode" in job or "cache-mode" in doc
        if not explicit: continue
        raw=job.get("cache-mode",doc.get("cache-mode"))
        if not isinstance(raw,str):
            out.append(finding(p,"CACHE_MODE_INVALID","high",name,"cache-mode must be a string.")); continue
        mode=raw.strip().lower()
        if "$" in mode and "{{" in mode:
            out.append(finding(p,"CACHE_MODE_DYNAMIC","review",name,"Expression-derived cache-mode needs manual evaluation.")); continue
        if mode not in VALID:
            out.append(finding(p,"CACHE_MODE_INVALID","high",name,"cache-mode must be read, write, write-only or none.")); continue
        if mode in ("write","write-only") and risky:
            out.append(finding(p,"CACHE_WRITE_LOW_TRUST","high",name,"Explicit cache write capability on potentially untrusted event(s): "+", ".join(risky)))
        if mode=="none":
            steps=job.get("steps",[])
            if isinstance(steps,list):
                cache_step=any(isinstance(step,dict) and (
                    str(step.get("uses","")).startswith("actions/cache@") or
                    (isinstance(step.get("with"),dict) and "cache" in step["with"]))
                    for step in steps)
                if cache_step: out.append(finding(p,"CACHE_STEPS_DISABLED","review",name,"Cache-related step may not operate under cache-mode none."))
    return out

def scan(target):
    out=[]
    for p in paths(target):
        if p.stat().st_size>LIMIT: raise ValueError("YAML file exceeds 2 MiB: "+str(p))
        try: docs=list(yaml.load_all(p.read_text(encoding="utf-8"),Loader=yaml.BaseLoader))
        except (UnicodeError,yaml.YAMLError) as exc: raise ValueError("invalid YAML: "+str(p)) from exc
        if len(docs)!=1: raise ValueError("workflow requires exactly one YAML document: "+str(p))
        out.extend(inspect(docs[0],p))
    return sorted(out,key=lambda x:(x["path"],x["location"],x["rule"]))

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path",type=Path); ap.add_argument("--json",action="store_true")
    args=ap.parse_args(argv)
    try: found=scan(args.path)
    except (OSError,ValueError) as e:
        print("Audit input error: "+str(e),file=sys.stderr); return 2
    if args.json: print(json.dumps({"count":len(found),"findings":found},indent=2))
    else:
        for item in found: print("{path} {location} [{severity}] {rule}: {message}".format(**item))
        print("Findings:",len(found))
    return 1 if found else 0
if __name__=="__main__": sys.exit(main())
