"""Read-only manifest HPA request contract review; no Kubernetes access."""
import argparse
import json
from pathlib import Path
import sys
import yaml

TARGETS = {"Deployment","StatefulSet","DaemonSet","ReplicaSet","ReplicationController"}

def read(path):
    root=Path(path)
    if not root.exists() or root.is_symlink():
        raise ValueError("input missing or symlink")
    sources=sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in (".yaml",".yml")) if root.is_dir() else [root]
    if not sources or len(sources)>500:
        raise ValueError("expected 1-500 YAML files")
    out=[]
    for p in sources:
        if p.stat().st_size>2000000:
            raise ValueError("2 MB file limit exceeded")
        try:
            for n,doc in enumerate(yaml.safe_load_all(p.read_text(encoding="utf-8")),1):
                if doc is None:
                    continue
                if not isinstance(doc,dict):
                    raise ValueError(f"{p}: document {n} is not a mapping")
                if isinstance(doc.get("kind"),str):
                    out.append((str(p),doc))
        except yaml.YAMLError as exc:
            raise ValueError(f"{p}: invalid YAML {type(exc).__name__}") from exc
    return out

def ns(obj):
    return (obj.get("metadata") or {}).get("namespace") or "default"

def identity(obj):
    return (ns(obj),obj.get("kind"),(obj.get("metadata") or {}).get("name"))

def containers(obj):
    return [c for c in (((obj.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers",[]) if isinstance(c,dict)]

def audit(documents):
    workloads={identity(o): (p,o) for p,o in documents if o.get("kind") in TARGETS and identity(o)[2]}
    findings=[]
    seen=set()
    def flag(code,path,obj,why):
        findings.append({"code":code,"file":path,"object":"/".join(str(x) for x in identity(obj)),"message":why})
    for path,hpa in documents:
        if hpa.get("kind")!="HorizontalPodAutoscaler":
            continue
        if hpa.get("apiVersion")!="autoscaling/v2":
            flag("HP000",path,hpa,"Only autoscaling/v2 analyzed; check other API versions manually")
            continue
        spec=hpa.get("spec") or {}
        if not isinstance(spec,dict):
            raise ValueError(f"{path}: spec must be mapping")
        mn,mx=spec.get("minReplicas",1),spec.get("maxReplicas")
        if isinstance(mn,bool) or not isinstance(mn,int) or mn<0 or isinstance(mx,bool) or not isinstance(mx,int) or mx<1 or mn>mx:
            flag("HP001",path,hpa,"Invalid replica bounds; min=0 needs feature-specific review")
        ref=spec.get("scaleTargetRef") or {}
        if not isinstance(ref,dict) or not all(ref.get(x) for x in ("kind","name","apiVersion")):
            flag("HP002",path,hpa,"Incomplete scaleTargetRef")
            continue
        target=(ns(hpa),ref["kind"],ref["name"])
        if target in seen:
            flag("HP003",path,hpa,"Multiple supplied HPAs target same workload")
        seen.add(target)
        if target not in workloads:
            flag("HP004",path,hpa,"Target workload not supplied (not proof it is missing live)")
            continue
        wpath,workload=workloads[target]
        members=containers(workload)
        if not members:
            flag("HP005",path,hpa,f"No inspectable containers in supplied {wpath}")
            continue
        metrics=spec.get("metrics") or []
        if not isinstance(metrics,list):
            raise ValueError(f"{path}: metrics must be list")
        for metric in metrics:
            if not isinstance(metric,dict):
                continue
            typ=metric.get("type")
            value=metric.get("resource") if typ=="Resource" else metric.get("containerResource") if typ=="ContainerResource" else None
            if not isinstance(value,dict):
                continue
            res=value.get("name")
            if res not in ("cpu","memory") or (value.get("target") or {}).get("type")!="Utilization":
                continue
            group=members
            if typ=="ContainerResource":
                group=[c for c in members if c.get("name")==value.get("container")]
                if not group:
                    flag("HP006",path,hpa,f"Unknown ContainerResource container {value.get('container')!r}")
                    continue
            for c in group:
                requests=((c.get("resources") or {}).get("requests") or {})
                if not isinstance(requests,dict) or not requests.get(res):
                    flag("HP007",path,hpa,f"Missing {res} request in container {c.get('name','<unnamed>')}")
    return sorted(findings,key=lambda x:(x["file"],x["object"],x["code"],x["message"]))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("path")
    p.add_argument("--json",action="store_true")
    args=p.parse_args(argv)
    try:
        findings=audit(read(args.path))
    except (OSError,UnicodeError,ValueError) as exc:
        print(f"Input error: {exc}",file=sys.stderr)
        return 2
    report={"count":len(findings),"findings":findings,"scope":"offline supplied manifests only; no live cluster checks"}
    if args.json:
        print(json.dumps(report,sort_keys=True))
    else:
        for f in findings:
            print(f"{f['code']} {f['file']} {f['object']}: {f['message']}")
        print(f"{len(findings)} finding(s)")
    return int(bool(findings))

if __name__=="__main__":
    sys.exit(main())
