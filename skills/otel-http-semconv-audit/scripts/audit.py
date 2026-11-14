#!/usr/bin/env python3
"""Offline HTTP semantic-convention migration review of sanitized OTLP JSON spans."""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_BYTES=4*1024*1024
MAX_SPANS=10000
LEGACY={
    "http.method":"http.request.method",
    "http.status_code":"http.response.status_code",
    "http.url":"url.full",
    "http.scheme":"url.scheme",
    "http.target":"url.path",
    "net.peer.name":"server.address",
    "net.peer.port":"server.port",
    "http.user_agent":"user_agent.original",
}
HTTP_KEYS=set(LEGACY)|set(LEGACY.values())|{"http.route","http.request.body.size","http.response.body.size"}
UUID=re.compile(r"(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
NUMBER_SEGMENT=re.compile(r"/[0-9]{5,}(?:/|$)")

class InputError(ValueError):
    pass

def load(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise InputError("expected a non-symlink JSON file no larger than 4 MiB")
    return json.loads(path.read_text(encoding="utf-8"))

def extract(payload):
    if not isinstance(payload,dict):
        raise InputError("JSON root must be a mapping")
    if "spans" in payload:
        groups=[payload["spans"]]
    elif "resourceSpans" in payload:
        resources=payload["resourceSpans"]
        if not isinstance(resources,list): raise InputError("resourceSpans must be an array")
        groups=[]
        for resource in resources:
            if not isinstance(resource,dict): raise InputError("resourceSpans item must be an object")
            scopes=resource.get("scopeSpans",resource.get("instrumentationLibrarySpans",[]))
            if not isinstance(scopes,list): raise InputError("scopeSpans must be an array")
            for scope in scopes:
                if not isinstance(scope,dict): raise InputError("scopeSpans item must be an object")
                groups.append(scope.get("spans",[]))
    else:
        raise InputError("expected spans or resourceSpans JSON structure")
    spans=[]
    for group in groups:
        if not isinstance(group,list): raise InputError("spans must be arrays")
        if any(not isinstance(item,dict) for item in group):
            raise InputError("spans must contain objects")
        spans.extend(group)
        if len(spans)>MAX_SPANS: raise InputError("more than 10000 spans")
    return spans

def attributes(span):
    raw=span.get("attributes",[])
    if isinstance(raw,dict):
        return {str(k):v for k,v in raw.items()}
    if not isinstance(raw,list): raise InputError("attributes must be array or mapping")
    result={}
    for attribute in raw:
        if not isinstance(attribute,dict) or not isinstance(attribute.get("key"),str):
            raise InputError("invalid OTLP attribute")
        result[attribute["key"]]=attribute.get("value")
    return result

def string_value(value):
    if isinstance(value,dict): return value.get("stringValue",None)
    return value if isinstance(value,str) else None

def analyze(payload,mode="unknown"):
    if mode not in ("unknown","http","http/dup"):
        raise InputError("invalid stability mode")
    spans=extract(payload)
    findings=[]
    analyzed=0
    def add(rule,severity,index,keys,detail):
        findings.append({"rule":rule,"severity":severity,"span_index":index,
                         "attribute_keys":sorted(keys),"detail":detail})
    for index,span in enumerate(spans):
        attrs=attributes(span)
        keys=set(attrs)
        relevant=bool(keys & HTTP_KEYS) or any(k.startswith("http.") for k in keys)
        if not relevant: continue
        analyzed+=1
        legacy=sorted(k for k in LEGACY if k in keys)
        if legacy and mode!="http/dup":
            add("OTEL_HTTP_LEGACY_KEYS","review",index,legacy,
                "legacy HTTP attributes may need migration to stable conventions")
        dual=sorted(k for k,stable in LEGACY.items() if k in keys and stable in keys)
        if dual and mode!="http/dup":
            add("OTEL_HTTP_DUAL_EMISSION","review",index,dual,
                "old and stable HTTP keys coexist; review intended stability mode")
        if mode=="http" and legacy:
            add("OTEL_HTTP_OPT_IN_CONFLICT","high",index,legacy,
                "legacy keys observed despite declared stable-only HTTP mode")
        route=string_value(attrs.get("http.route"))
        if isinstance(route,str) and (UUID.search(route) or NUMBER_SEGMENT.search(route)):
            add("OTEL_HTTP_ROUTE_CARDINALITY","review",index,["http.route"],
                "route may include raw identifiers; inspect low-cardinality route template")
    return {"count":len(findings),"http_spans":analyzed,"total_spans":len(spans),
            "mode":mode,"findings":findings,
            "note":"attribute values are never included; samples do not prove production configuration"}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",help="local sanitized OTLP JSON trace export")
    parser.add_argument("--stability-opt-in",choices=["unknown","http","http/dup"],default="unknown")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args(argv)
    try:
        result=analyze(load(args.input),args.stability_opt_in)
    except (OSError,UnicodeError,ValueError,json.JSONDecodeError) as exc:
        print("INPUT ERROR: "+str(exc),file=sys.stderr)
        return 2
    if args.json: print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print(str(result["count"])+" finding(s) across "+str(result["http_spans"])+" HTTP spans")
        for f in result["findings"]:
            print(f["severity"]+": "+f["rule"]+" at span #"+str(f["span_index"]))
    return 1 if result["count"] else 0

if __name__=="__main__":
    sys.exit(main())
