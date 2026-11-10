# Diagnostic reference

| Code | Meaning |
|---|---|
| BK001 | Could not safely tokenize ARG/ENV syntax. |
| BK002 | Credential-like variable declared via ARG/ENV. |
| BK003 | Secret mount has neither id nor target. |
| BK004 | Secret mount is optional; required=true may be appropriate. |
| BK005 | RUN mentions a sensitive-looking shell variable without a secret mount in that instruction. |
| BK006 | COPY/ADD mentions credential-like path; review `.dockerignore` and build context. |
| BK007 | ADD URL contains a username/password userinfo pattern. |

Findings are offline heuristics, not confirmed secret leaks. BK004 is reliability advice, not a proof of security vulnerability. Neither image history nor actual build invocation is inspected. Nondefault Dockerfile escape directives are rejected to avoid unsafe parsing. Input contents and secret values are not echoed.
