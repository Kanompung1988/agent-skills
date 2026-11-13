#!/usr/bin/env python3
"""Offline StatefulSet PVC retention and template audit."""
import argparse
import json
import sys
from pathlib import Path
import yaml

LIMIT=2*1024*1024

def paths(target):
    if target.is_symlink(): raise ValueError("symlink input not supported")
    if target.is_file(): return [target]
    if not target.is_dir(): raise ValueError("expected a YAML file or directory")
    return sorted(p for p in target.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in (".yml",".yaml"))

def inspect(doc,p):
    if doc is None or doc == "": return []
    if not isinstance(doc,dict): raise ValueError("Kubernetes manifest root must be a mapping")
    if doc.get("kind")!="StatefulSet": return []
    meta=doc.get("metadata") if isinstance(doc.get("metadata"),dict) else {}
    name=str(meta.get("name","<unnamed>"))
    ns=str(meta.get("namespace","default"))
    spec=doc.get("spec")
    if not isinstance(spec,dict): raise ValueError("StatefulSet spec must be a mapping")
    out=[]
    def add(rule,sev,msg):
        out.append({"path":str(p),"rule":rule,"severity":sev,"resource":name,"namespace":ns,"message":msg})
    if doc.get("apiVersion")!="apps/v1":
        add("STS_VERSION_REVIEW","review","This analyzer targets apps/v1 StatefulSets.")
    templates=spec.get("volumeClaimTemplates",[])
    if not isinstance(templates,list): raise ValueError("volumeClaimTemplates must be a list")
    seen=set()
    for i,item in enumerate(templates):
        if not isinstance(item,dict):
            add("PVC_TEMPLATE_INVALID","high","Claim template "+str(i)+" must be a mapping."); continue
        imeta=item.get("metadata") if isinstance(item.get("metadata"),dict) else {}
        claim=imeta.get("name")
        if not isinstance(claim,str) or not claim.strip():
            add("PVC_TEMPLATE_UNNAMED","high","Claim template "+str(i)+" has no metadata.name.")
        elif claim in seen:
            add("PVC_TEMPLATE_DUPLICATE","high","Repeated claim template name: "+claim)
        else: seen.add(claim)
        ispec=item.get("spec") if isinstance(item.get("spec"),dict) else {}
        res=ispec.get("resources") if isinstance(ispec.get("resources"),dict) else {}
        req=res.get("requests") if isinstance(res.get("requests"),dict) else {}
        if not isinstance(req.get("storage"),str) or not req.get("storage","").strip():
            add("PVC_STORAGE_REQUEST_MISSING","high","Claim template "+str(i)+" lacks resources.requests.storage.")
    policy=spec.get("persistentVolumeClaimRetentionPolicy",{})
    if not isinstance(policy,dict):
        add("PVC_POLICY_MALFORMED","high","Retention policy must be a mapping."); return out
    for field in policy:
        if field not in ("whenDeleted","whenScaled"):
            add("PVC_POLICY_UNKNOWN_FIELD","high","Unknown policy field: "+str(field))
    for field,rule in (("whenDeleted","PVC_DELETE_ON_SET_REMOVAL"),("whenScaled","PVC_DELETE_ON_SCALE_DOWN")):
        value=policy.get(field,"Retain")
        if value not in ("Retain","Delete"):
            add("PVC_POLICY_INVALID_VALUE","high",field+" must be Retain or Delete (default Retain).")
        elif value=="Delete" and templates:
            add(rule,"high","Generated PVCs may be deleted after "+("StatefulSet deletion" if field=="whenDeleted" else "scale-down")+". Review backups and retention requirements.")
    if policy and not templates:
        add("PVC_POLICY_WITHOUT_TEMPLATES","review","Policy only applies to generated volumeClaimTemplates.")
    return out

def scan(target):
    result=[]
    for p in paths(target):
        if p.stat().st_size>LIMIT: raise ValueError("YAML file exceeds 2 MiB: "+str(p))
        try: docs=list(yaml.load_all(p.read_text(encoding="utf-8"),Loader=yaml.BaseLoader))
        except (UnicodeError,yaml.YAMLError) as exc: raise ValueError("invalid YAML: "+str(p)) from exc
        for doc in docs: result.extend(inspect(doc,p))
    return sorted(result,key=lambda x:(x["path"],x["namespace"],x["resource"],x["rule"]))

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path",type=Path); ap.add_argument("--json",action="store_true")
    args=ap.parse_args(argv)
    try: found=scan(args.path)
    except (OSError,ValueError) as exc:
        print("Audit input error: "+str(exc),file=sys.stderr); return 2
    if args.json: print(json.dumps({"count":len(found),"findings":found},indent=2))
    else:
        for item in found: print("{path} {namespace}/{resource} [{severity}] {rule}: {message}".format(**item))
        print("Findings:",len(found))
    return 1 if found else 0
if __name__=="__main__": sys.exit(main())
