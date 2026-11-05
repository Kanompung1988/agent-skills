#!/usr/bin/env python3
"""Bounded, offline audit of nginx add_header inheritance. Python 3.10+ stdlib only."""
import argparse
import json
import re
import sys
from pathlib import Path

SECURITY = {"strict-transport-security", "content-security-policy", "x-content-type-options",
            "x-frame-options", "referrer-policy", "permissions-policy",
            "cross-origin-opener-policy", "cross-origin-resource-policy"}
MAX_BYTES = 2_000_000


def tokenize(source):
    """Tokenize nginx syntax, honoring comments, quotes and escaped punctuation."""
    result, word, line, start, quote, escaped, comment = [], [], 1, 1, None, False, False

    def flush():
        nonlocal word
        if word:
            result.append(("".join(word), start))
            word = []

    for char in source:
        if char == "\n":
            if comment:
                comment = False
                line += 1
                continue
            if quote:
                word.append(char)
            else:
                flush()
            line += 1
            continue
        if comment:
            continue
        if escaped:
            word.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            if not word:
                start = line
            continue
        if quote:
            if char == quote:
                quote = None
            else:
                word.append(char)
            continue
        if char in "'\"":
            if not word:
                start = line
            quote = char
            continue
        if char == "#":
            flush()
            comment = True
            continue
        if char.isspace():
            flush()
            continue
        if char in "{};":
            flush()
            result.append((char, line))
            continue
        if not word:
            start = line
        word.append(char)
    if quote:
        raise ValueError("Unclosed quoted string")
    if escaped:
        raise ValueError("Dangling escape at EOF")
    flush()
    return result


def parse(text):
    tokens = tokenize(text)
    position = 0

    def context(expect_close=False):
        nonlocal position
        statements, current = [], []
        while position < len(tokens):
            token, line = tokens[position]
            position += 1
            if token == "}":
                if not expect_close or current:
                    raise ValueError(f"Unexpected closing brace at line {line}")
                return statements
            if token == ";":
                if not current:
                    raise ValueError(f"Empty directive at line {line}")
                statements.append({"args": current, "line": current[0][1], "children": None})
                current = []
                continue
            if token == "{":
                if not current:
                    raise ValueError(f"Unlabeled block at line {line}")
                child = context(True)
                statements.append({"args": current, "line": current[0][1], "children": child})
                current = []
                continue
            current.append((token, line))
        if expect_close:
            raise ValueError("Unclosed nginx block")
        if current:
            raise ValueError(f"Unterminated directive at line {current[0][1]}")
        return statements

    return context()


def audit_text(text, nginx_version=None):
    nodes = parse(text)
    findings = []

    def finding(rule, line, context, detail):
        findings.append({"rule": rule, "line": line, "context": context, "message": detail})

    def walk(body, inherited, mode, context):
        local = [s for s in body if s["children"] is None and s["args"][0][0] == "add_header"]
        inheritance = [s for s in body if s["children"] is None and s["args"][0][0] == "add_header_inherit"]
        current_mode = mode
        if inheritance:
            entry = inheritance[-1]
            values = [v for v, _ in entry["args"]]
            if len(values) != 2 or values[1] not in ("on", "off", "merge"):
                finding("NGH004", entry["line"], context, "Invalid add_header_inherit mode")
            else:
                current_mode = values[1]
                if nginx_version is not None and nginx_version < (1, 29, 3):
                    finding("NGH005", entry["line"], context, "add_header_inherit requires nginx >=1.29.3")
        found = []
        for statement in local:
            values = [v for v, _ in statement["args"]]
            if len(values) not in (3, 4) or (len(values) == 4 and values[-1] != "always"):
                finding("NGH006", statement["line"], context, "Unrecognized add_header directive shape")
                continue
            name = values[1].lower()
            found.append((name, statement["line"]))
            if name in SECURITY and values[-1] != "always":
                finding("NGH002", statement["line"], context, f"{name} lacks 'always' (not applied to all response codes)")
        # Inheritance mode is itself inherited; local add_header normally replaces all parent headers.
        if current_mode == "off":
            effective = found
        elif current_mode == "merge":
            effective = inherited + found
        elif local:
            effective = found
        else:
            effective = inherited
        parent_security = {name for name, _ in inherited if name in SECURITY}
        effective_security = {name for name, _ in effective if name in SECURITY}
        lost = sorted(parent_security - effective_security)
        if lost:
            line = local[0]["line"] if local else (inheritance[-1]["line"] if inheritance else 1)
            finding("NGH001", line, context,
                    "Inherited security header(s) no longer effective: " + ", ".join(lost))
        for statement in body:
            values = [v for v, _ in statement["args"]]
            if statement["children"] is None and values[0] == "include":
                finding("NGH003", statement["line"], context, "Unexpanded include; inspect included configuration separately")
            if statement["children"] is not None:
                child = values[0] + (" " + " ".join(values[1:]) if len(values) > 1 else "")
                walk(statement["children"], effective, current_mode, context + "/" + child)
    walk(nodes, [], "on", "root")
    findings.sort(key=lambda f: (f["line"], f["rule"], f["context"]))
    return findings


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("file", type=Path)
    cli.add_argument("--json", action="store_true")
    cli.add_argument("--nginx-version", help="nginx version such as 1.29.3; enables feature gate")
    args = cli.parse_args(argv)
    try:
        if not args.file.is_file() or args.file.stat().st_size > MAX_BYTES:
            raise ValueError("Expected a regular nginx config file up to 2MB")
        data = args.file.read_text(encoding="utf-8")
        version = None
        if args.nginx_version is not None:
            if not re.fullmatch(r"\d+\.\d+\.\d+", args.nginx_version):
                raise ValueError("Expected --nginx-version MAJOR.MINOR.PATCH")
            version = tuple(map(int, args.nginx_version.split(".")))
        findings = audit_text(data, version)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        print(f"{len(findings)} finding(s)")
        for f in findings:
            print(f"{f['rule']} line {f['line']} {f['context']}: {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
