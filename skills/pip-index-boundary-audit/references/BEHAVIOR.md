# Behaviour and scope

**Source:** [pip install docs](https://pip.pypa.io/en/stable/cli/pip_install/) explicitly warn that `--extra-index-url` can enable dependency confusion by allowing same-named packages on a public index.

This tool checks requirements files and includes only. Recognizes `--index-url`, `--extra-index-url`, `--trusted-host`, `--no-index`, `-r` and `-c` and emits only rule codes and file locations. Handles recursion with an 8-level cap, a per-file 1 MB limit and restricts include targets to the supplied root. Never prints package-index URL values or credentials.

No shell execution, pip install, index queries, dependency resolver simulation, pip.conf, pyproject tool.pip sections, env variables or automatic package policy. A warning does not prove compromise. A clean result does not prove safe resolution. Editability of included files is considered a trust-boundary concern.
