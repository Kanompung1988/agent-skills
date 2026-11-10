"""Read-only Dockerfile build-secret boundary scanner."""
import argparse
import json
import re
import shlex
import sys
from pathlib import Path

SECRET=re.compile(r"(?:^|_)(?:SECRET|PASSWORD|TOKEN|CREDENTIALS?|PRIVATE_KEY|API_KEY|ACCESS_KEY|AUTH_TOKEN)(?:_|$)",re.I)
MOUNTS=re.compile(r"--mount=([^\s]+)",re.I)
VARIABLE=re.compile(r"\$(?:\{([A-Za-z_][\w]*)\}|([A-Za-z_][\w]*))")
COPY_SECRET=re.compile(r"(?:^|[/\s])(?:\.npmrc|\.pypirc|id_rsa|\.env(?:\.[\w.-]+)?)(?:[/\s]|$)",re.I)

def issue(code,path,line,message):
    return dict(code=code,file=str(path),line=line,message=message)

def instructions(text):
    buffer=""
    for lineno,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not buffer:
            start=lineno
        if not line or (line.startswith("#") and not buffer):
            continue
        continued=line.endswith("\\")
        buffer+=line[:-1].rstrip()+" " if continued else line
        if not continued:
            yield start,buffer.strip()
            buffer=""
    if buffer: yield start,buffer.strip()

def parse(path):
    if path.is_symlink(): return [],"symlink not supported"
    try:
        if path.stat().st_size>2_000_000: return [],"Dockerfile exceeds 2 MB"
        text=path.read_text(encoding="utf-8")
    except (OSError,UnicodeError):
        return [],"unreadable UTF-8 input"
    if re.search(r"(?im)^\s*#\s*escape\s*=\s*\x60",text):
        return [],"non-default Dockerfile escape directive unsupported"
    findings=[]
    for line,statement in instructions(text):
        parts=statement.split(None,1)
        if len(parts)<2: continue
        op,argument=parts[0].upper(),parts[1]
        if op in ("ARG","ENV"):
            try: tokens=shlex.split(argument)
            except ValueError:
                findings.append(issue("BK001",path,line,"unparseable ARG/ENV declaration"))
                continue
            if op=="ARG":
                names=[tokens[0].split("=",1)[0]] if tokens else []
            elif tokens and "=" in tokens[0]:
                names=[x.split("=",1)[0] for x in tokens if "=" in x]
            else:
                names=tokens[:1]
            if any(SECRET.search(x) for x in names):
                findings.append(issue("BK002",path,line,"secret-like variable declared with ARG/ENV; prefer BuildKit mount"))
        if op=="RUN":
            mounts=[]
            for match in MOUNTS.findall(argument):
                fields={}
                for item in match.split(","):
                    k,separator,v=item.partition("=")
                    if separator: fields[k.lower()]=v
                if fields.get("type","").lower()=="secret":
                    mounts.append(fields)
                    if not fields.get("id") and not any(fields.get(x) for x in ("target","dst","destination")):
                        findings.append(issue("BK003",path,line,"secret mount lacks both id and target"))
                    if fields.get("required","false").lower() not in ("true","1"):
                        findings.append(issue("BK004",path,line,"secret mount is optional; consider required=true for reliability"))
            variables={x or y for x,y in VARIABLE.findall(argument)}
            if any(SECRET.search(x) for x in variables) and not mounts:
                findings.append(issue("BK005",path,line,"RUN uses secret-like variable without an in-instruction BuildKit secret mount"))
        if op in ("COPY","ADD"):
            if COPY_SECRET.search(" "+argument+" "):
                findings.append(issue("BK006",path,line,"COPY/ADD references sensitive-looking file; inspect context exposure"))
            if re.search(r"https?://[^\s/@]+:[^\s/@]+@",argument,re.I):
                findings.append(issue("BK007",path,line,"ADD uses URL with userinfo credentials"))
    return findings,None

def scan(paths):
    candidates=set()
    findings,errors=[],[]
    for path in map(Path,paths):
        if path.is_symlink(): errors.append(f"{path}: symlink blocked")
        elif path.is_file(): candidates.add(path)
        elif path.is_dir():
            candidates.update(x for x in path.rglob("*") if x.is_file() and not x.is_symlink() and (x.name=="Dockerfile" or x.name.startswith("Dockerfile.")))
        else: errors.append(f"{path}: missing file or folder")
    for path in sorted(candidates):
        f,error=parse(path)
        findings+=f
        if error: errors.append(f"{path}: {error}")
    findings.sort(key=lambda x:(x["file"],x["line"],x["code"]))
    return dict(files_scanned=len(candidates),findings=findings,errors=errors,limitations="Static Dockerfile only; no build invocation, registry state or image layer inspection")

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths",nargs="+")
    p.add_argument("--json",action="store_true")
    args=p.parse_args(argv)
    data=scan(args.paths)
    if args.json: print(json.dumps(data,indent=2,sort_keys=True))
    else:
        print(f'{data["files_scanned"]} files, {len(data["findings"])} findings, {len(data["errors"])} errors')
        for x in data["findings"]: print(f'{x["file"]}:{x["line"]} {x["code"]}: {x["message"]}')
        for x in data["errors"]: print(x,file=sys.stderr)
    return 2 if data["errors"] else 1 if data["findings"] else 0

if __name__=="__main__":
    raise SystemExit(main())
