#!/usr/bin/env python3
"""Read-only, local Git submodule declaration versus index gitlink audit.

Never clones, fetches, initializes, updates, or executes any submodule content.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

def git(root, *args, input_bytes=None, allowed=(0,)):
    run = subprocess.run(["git", "-C", str(root), *args], input=input_bytes,
                         capture_output=True, check=False, timeout=15)
    if run.returncode not in allowed:
        msg = run.stderr.decode("utf-8", "replace").strip()
        raise ValueError("git command failed: " + (msg[:250] or str(run.returncode)))
    return run.stdout

def parse_modules(raw):
    if not raw:
        return {}
    out = git(".", "config", "--null", "-f", "-", "--list", input_bytes=raw)
    sections = {}
    for entry in out.split(b"\0"):
        if not entry:
            continue
        key, sep, value = entry.partition(b"\n")
        if not sep:
            raise ValueError("Invalid git config serialization")
        key = key.decode("utf-8", "replace")
        m = re.fullmatch(r"submodule\.(.+)\.(path|url|branch|update)", key)
        if m:
            sections.setdefault(m.group(1), {})[m.group(2)] = value.decode("utf-8", "replace")
    return sections

def index_entries(root):
    raw = git(root, "ls-files", "--stage", "-z")
    entries = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        meta, sep, path = entry.partition(b"\t")
        if not sep:
            raise ValueError("Invalid git index entry")
        parts = meta.split()
        if len(parts) != 3:
            raise ValueError("Invalid git index header")
        mode, sha, stage = parts
        if stage != b"0":
            raise ValueError("Unmerged index entry: audit requires resolved index")
        entries[path.decode("utf-8", "surrogateescape")] = (mode.decode("ascii"), sha.decode("ascii"))
    return entries

def unsafe_path(path):
    if not path or path.startswith("/") or "\\" in path:
        return True
    parts=path.split("/")
    return any(x in ("", ".", "..", ".git") for x in parts) or "\x00" in path

def url_issue(url):
    # Git can use local paths, Git protocols, relative URLs, scp syntax or HTTPS.
    if not url:
        return "MISSING_URL"
    if url.startswith(("/", "~")) or url.startswith("file://"):
        return "LOCAL_SOURCE"
    if url.startswith("http://") or url.startswith("git://"):
        return "UNENCRYPTED_TRANSPORT"
    if url.startswith(("./", "../")):
        return None  # Supported upstream-relative source; review its base remote separately.
    scheme=urlsplit(url).scheme
    if scheme and scheme not in ("https", "ssh"):
        return "UNRECOGNIZED_SCHEME"
    if not scheme and not re.fullmatch(r"[^/:\s]+@[^/:\s]+:.+",url):
        return "AMBIGUOUS_SOURCE"
    return None

def audit(repo):
    root=Path(repo).resolve()
    git(root,"rev-parse","--show-toplevel")
    index=index_entries(root)
    gitlinks={path:sha for path,(mode,sha) in index.items() if mode=="160000"}
    raw=git(root,"show",":.gitmodules",allowed=(0,128)) if ".gitmodules" in index else b""
    modules=parse_modules(raw)
    findings=[]
    def flag(code,path,severity,explanation):
        findings.append(dict(code=code, path=path, severity=severity, message=explanation))
    seen_paths={}
    for name, data in sorted(modules.items()):
        path=data.get("path","")
        if unsafe_path(path):
            flag("INVALID_PATH",name,"high","Submodule path is missing, absolute, traversing or malformed")
            continue
        if path in seen_paths:
            flag("DUPLICATE_PATH",path,"high","Multiple .gitmodules sections claim one path")
        seen_paths[path]=name
        if path not in gitlinks:
            flag("MISSING_GITLINK",path,"high","Declared path has no stage-0 mode-160000 index entry")
        issue=url_issue(data.get("url",""))
        if issue:
            flag(issue,path,"high" if issue != "AMBIGUOUS_SOURCE" else "review",
                 "Submodule source URL requires review before initialization")
        if data.get("branch"):
            flag("REMOTE_TRACKING_OPTION",path,"advisory",
                 ".gitmodules branch affects 'git submodule update --remote', NOT normal pinned gitlinks")
        if data.get("update") in ("rebase","merge"):
            flag("NONCHECKOUT_UPDATE",path,"review",
                 "Submodule update mode may integrate local commits instead of checkout")
        elif data.get("update") and data["update"] not in ("checkout", "none"):
            flag("UNKNOWN_UPDATE",path,"high","Invalid or unsupported update mode in .gitmodules")
    for path in sorted(set(gitlinks)-set(seen_paths)):
        flag("UNDECLARED_GITLINK",path,"high","Index gitlink lacks a corresponding .gitmodules path")
    return dict(repository=str(root), gitlink_count=len(gitlinks), declared=len(modules),
                count=len(findings), findings=findings,
                note="Index declarations only. Gitlinks are commit-pinned; no remote identity, signature, reachability or checkout verification.")

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repository",nargs="?",default=".",help="Local Git superproject path")
    p.add_argument("--json",action="store_true")
    a=p.parse_args(argv)
    try:
        r=audit(a.repository)
    except (ValueError,OSError,subprocess.TimeoutExpired,UnicodeError) as exc:
        print(f"input error: {exc}",file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r,indent=2,sort_keys=True))
    else:
        print(f"{r['declared']} declarations, {r['gitlink_count']} gitlinks, {r['count']} findings")
        for f in r["findings"]:
            print(f"{f['severity']}: {f['path']} {f['code']}: {f['message']}")
    return 1 if r["count"] else 0

if __name__=="__main__":
    sys.exit(main())
