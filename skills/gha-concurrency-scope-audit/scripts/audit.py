"""Offline GitHub Actions concurrency audit. Never executes workflow or contacts GitHub."""
import argparse
import json
import sys
from pathlib import Path
import yaml

def report(code,path,scope,message):
    return {"code":code,"file":str(path),"scope":scope,"message":message}

def scan(paths):
    findings, errors, groups = [], [], {}
    candidates=set()
    for path in map(Path,paths):
        if path.is_symlink():
            errors.append(f"{path}: symlink not allowed")
        elif path.is_file():
            candidates.add(path)
        elif path.is_dir():
            candidates.update(p for p in path.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in (".yaml",".yml"))
        else:
            errors.append(f"{path}: missing input")
    dynamic=0
    for path in sorted(candidates):
        try:
            if path.stat().st_size>2_000_000: raise ValueError("oversized file")
            root=yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(root,dict): raise ValueError("root not mapping")
            jobs=root.get("jobs") or {}
            if not isinstance(jobs,dict): raise ValueError("jobs not mapping")
        except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f"{path}: invalid input ({type(exc).__name__})")
            continue
        contexts=[("workflow",root["concurrency"])] if "concurrency" in root else []
        contexts.extend((f"job:{name}",data["concurrency"]) for name,data in jobs.items() if isinstance(data,dict) and "concurrency" in data)
        for scope,entry in contexts:
            if isinstance(entry,str):
                group,cancel,queue=entry,False,"single"
            elif isinstance(entry,dict):
                group=entry.get("group")
                cancel=entry.get("cancel-in-progress",False)
                queue=entry.get("queue","single")
            else:
                findings.append(report("CC001",path,scope,"concurrency must be string or mapping"))
                continue
            if not isinstance(group,str) or not group.strip():
                findings.append(report("CC001",path,scope,"group must be a nonempty string"))
                continue
            if not isinstance(cancel,(bool,str)):
                findings.append(report("CC004",path,scope,"cancel-in-progress must be boolean or expression"))
            if not isinstance(queue,str) or (queue not in ("single","max") and "$"+"{{" not in queue):
                findings.append(report("CC005",path,scope,"unsupported queue value"))
            if queue=="max" and cancel is True:
                findings.append(report("CC002",path,scope,"queue=max and cancel-in-progress=true conflict"))
            if cancel is True and any(t in (path.stem+" "+scope).lower() for t in ("release","deploy","publish","production")):
                findings.append(report("CC003",path,scope,"release scope cancels running work; confirm intent"))
            if "$"+"{{" in group:
                dynamic+=1
            else:
                groups.setdefault(group.strip().casefold(),[]).append((path,scope))
                if scope=="workflow" and queue=="single" and cancel is False:
                    findings.append(report("CC006",path,scope,"literal single queue replaces pending runs; review intent"))
    for participants in groups.values():
        if len(participants)>1:
            for path,scope in participants:
                findings.append(report("CC007",path,scope,"literal group shared across inspected scopes"))
    findings.sort(key=lambda d:(d["file"],d["scope"],d["code"]))
    return {"files_scanned":len(candidates),"findings":findings,"errors":errors,"dynamic_groups_unresolved":dynamic}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths",nargs="+")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args(argv)
    result=scan(args.paths)
    if args.json:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print(f'{result["files_scanned"]} scanned, {len(result["findings"])} review findings, {len(result["errors"])} input errors')
        for row in result["findings"]:
            print(f'{row["file"]} [{row["scope"]}] {row["code"]}: {row["message"]}')
        for error in result["errors"]: print(error,file=sys.stderr)
    return 2 if result["errors"] else 1 if result["findings"] else 0

if __name__=="__main__":
    raise SystemExit(main())
