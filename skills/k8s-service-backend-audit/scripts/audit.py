"""Offline Kubernetes Service selector and targetPort contract review."""
import argparse
import json
from pathlib import Path
import sys
import yaml

WORKLOADS={"Pod","Deployment","StatefulSet","DaemonSet","ReplicaSet","ReplicationController","Job","CronJob"}

def read(path):
    root=Path(path)
    if not root.exists() or root.is_symlink():
        raise ValueError("input missing or symlink")
    paths=sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() in (".yaml",".yml")) if root.is_dir() else [root]
    if not paths or len(paths)>500:
        raise ValueError("expected 1-500 YAML files")
    result=[]
    for p in paths:
        if p.stat().st_size>2000000:
            raise ValueError("2 MB file size limit exceeded")
        try:
            for idx,obj in enumerate(yaml.safe_load_all(p.read_text(encoding="utf-8")),1):
                if obj is None:
                    continue
                if not isinstance(obj,dict):
                    raise ValueError(f"{p}: document {idx} not mapping")
                if isinstance(obj.get("kind"),str):
                    result.append((str(p),obj))
        except yaml.YAMLError as exc:
            raise ValueError(f"{p}: invalid YAML {type(exc).__name__}") from exc
    return result

def ns(obj):
    return (obj.get("metadata") or {}).get("namespace") or "default"

def pod_shape(obj):
    if obj.get("kind")=="Pod":
        metadata=obj.get("metadata") or {}
        pod=obj.get("spec") or {}
    else:
        spec=obj.get("spec") or {}
        if obj.get("kind")=="CronJob":
            spec=((spec.get("jobTemplate") or {}).get("spec") or {})
        template=spec.get("template") or {}
        metadata=template.get("metadata") or {}
        pod=template.get("spec") or {}
    names=set()
    for container in pod.get("containers") or []:
        if isinstance(container,dict):
            for p in container.get("ports") or []:
                if isinstance(p,dict) and p.get("name"):
                    names.add(p["name"])
    return metadata.get("labels") or {},names

def audit(documents):
    workloads=[(p,o,*pod_shape(o)) for p,o in documents if o.get("kind") in WORKLOADS]
    findings=[]
    def flag(code,path,service,why):
        name=(service.get("metadata") or {}).get("name") or "<unnamed>"
        findings.append({"code":code,"file":path,"object":f"{ns(service)}/Service/{name}","message":why})
    for path,service in documents:
        if service.get("kind")!="Service":
            continue
        spec=service.get("spec") or {}
        if not isinstance(spec,dict):
            raise ValueError(f"{path}: Service spec must be mapping")
        if spec.get("type")=="ExternalName":
            continue
        selector=spec.get("selector")
        if selector is None or selector=={}:
            continue  # Valid selectorless Service may use manual EndpointSlices
        if not isinstance(selector,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in selector.items()):
            flag("SV001",path,service,"Selector must be a mapping of string keys and values")
            continue
        matched=[(p,o,ports) for p,o,labels,ports in workloads if ns(o)==ns(service) and isinstance(labels,dict) and all(labels.get(k)==v for k,v in selector.items())]
        if not matched:
            flag("SV002",path,service,"No supplied same-namespace Pod/template matches selector; input may be incomplete")
            continue
        ports=spec.get("ports") or []
        if not isinstance(ports,list):
            raise ValueError(f"{path}: spec.ports must be a list")
        for port in ports:
            if not isinstance(port,dict):
                continue
            target=port.get("targetPort",port.get("port"))
            if isinstance(target,str) and target:
                missing=[f"{o.get('kind')}/{(o.get('metadata') or {}).get('name','<unnamed>')}" for _,o,names in matched if target not in names]
                if missing:
                    flag("SV003",path,service,f"targetPort {target!r} missing on matched workload declarations: {', '.join(sorted(missing))}")
            elif isinstance(target,bool) or not isinstance(target,int) or not 1<=target<=65535:
                flag("SV004",path,service,"targetPort must be a valid integer or nonempty named port")
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
    output={"count":len(findings),"findings":findings,"scope":"offline input manifests, not live EndpointSlices or readiness"}
    if args.json:
        print(json.dumps(output,sort_keys=True))
    else:
        for f in findings:
            print(f"{f['code']} {f['file']} {f['object']}: {f['message']}")
        print(f"{len(findings)} finding(s)")
    return int(bool(findings))

if __name__=="__main__":
    sys.exit(main())
