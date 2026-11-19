#!/usr/bin/env python3
"""Conservative offline PostgreSQL SECURITY DEFINER search_path audit."""
import argparse
import json
import re
import sys
from pathlib import Path


def mask_and_split(source):
    """Mask comments, quoted literals, dollar bodies; split only SQL-level semicolons.

    Maintains exact text length for statement line offsets. Nested block comments
    and PostgreSQL dollar tags are supported; neither is parsed as active SQL.
    """
    cleaned = list(source)
    boundaries = []
    i, start, n = 0, 0, len(source)
    def mask(a, b):
        for j in range(a, b):
            if source[j] != "\n": cleaned[j] = " "
    while i < n:
        if source.startswith("--", i):
            j = source.find("\n", i)
            if j < 0: j = n
            mask(i, j); i = j; continue
        if source.startswith("/*", i):
            j, depth = i + 2, 1
            while j < n and depth:
                if source.startswith("/*", j): depth += 1; j += 2
                elif source.startswith("*/", j): depth -= 1; j += 2
                else: j += 1
            mask(i, j); i = j; continue
        if source[i] in ("'", '"'):
            quote = source[i]; j = i+1
            while j < n:
                if source[j] == quote:
                    if j+1 < n and source[j+1] == quote: j += 2; continue
                    j += 1; break
                j += 1
            # Double quoted schema identifiers should be inspected separately;
            # conservative: do not claim safe when quoted path values are used.
            mask(i, j); i = j; continue
        if source[i] == "$":
            m = re.match(r"\$[A-Za-z_][A-Za-z_0-9]*\$|\$\$", source[i:])
            if m:
                tag = m.group(0); at = source.find(tag, i+len(tag))
                j = n if at < 0 else at + len(tag)
                mask(i, j); i = j; continue
        if source[i] == ";":
            boundaries.append((start, i+1)); start = i+1
        i += 1
    if source[start:].strip(): boundaries.append((start, n))
    return "".join(cleaned), boundaries


def audit_sql(source):
    clean, boundaries = mask_and_split(source)
    findings = []
    for start, end in boundaries:
        statement = clean[start:end]
        m = re.search(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP(?:ORARY)?\s+)?(FUNCTION|PROCEDURE)\s+([^\s(]+)", statement, re.I)
        if not m: continue
        if not re.search(r"\bSECURITY\s+DEFINER\b", statement, re.I): continue
        line = source.count("\n", 0, start + m.start()) + 1
        func = m.group(2)
        def add(sev, code, message):
            findings.append({"severity": sev, "code": code,
                             "line": line, "routine": func, "message": message})
        sp = re.search(r"\bSET\s+search_path\s*(?:=|TO|FROM)\s*([^;]+?)(?=\b(?:LANGUAGE|SECURITY|COST|ROWS|PARALLEL|STRICT|IMMUTABLE|STABLE|VOLATILE|LEAKPROOF|AS|SET)\b|;|$)", statement, re.I | re.S)
        if not sp:
            add("high", "MISSING_SEARCH_PATH", "SECURITY DEFINER routine has no function-level SET search_path")
            continue
        raw = sp.group(1).strip().rstrip(",")
        # No guarantee that user-provided schemas are trusted. Quoted names and
        # FROM CURRENT / DEFAULT require manual review.
        if not raw or re.search(r"\b(CURRENT|FROM\s+CURRENT|DEFAULT)\b", raw, re.I) or '"' in source[start+sp.start(1):start+sp.end(1)]:
            add("review", "UNRESOLVED_SEARCH_PATH", "Search path cannot be confidently parsed; review effective schemas")
            continue
        names = [x.strip().lower() for x in raw.split(",")]
        if any(not re.fullmatch(r"[a-z_][a-z_0-9]*|\$user", name) for name in names):
            add("review", "UNRESOLVED_SEARCH_PATH", "Search path contains an expression or nontrivial schema name")
            continue
        if "public" in names or "$user" in names:
            add("review", "UNTRUSTED_SCHEMA_REVIEW", "Verify public/$user schemas are not writable by untrusted roles")
        if "pg_temp" not in names:
            add("review", "PG_TEMP_MISSING", "Explicit pg_temp-last guidance not met; inspect temp object resolution")
        elif names[-1] != "pg_temp":
            add("review", "PG_TEMP_ORDER", "pg_temp should be last in the search_path")
    return sorted(findings, key=lambda f: (f["line"], f["code"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql_file", type=Path, help="SQL migration or function definition")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--strict", action="store_true", help="Exit 2 on findings")
    args = parser.parse_args(argv)
    try:
        findings = audit_sql(args.sql_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['severity'].upper()} [{f['code']}] line {f['line']} {f['routine']}: {f['message']}")
        print(f"Findings: {len(findings)} (not proof of database security)")
    return 2 if args.strict and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
