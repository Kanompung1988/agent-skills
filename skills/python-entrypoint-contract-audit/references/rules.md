# Rules, source references and honest limits

PyPA PEP 621 / pyproject TOML specification: https://packaging.python.org/en/latest/specifications/pyproject-toml/ .
PyPA entry points: https://packaging.python.org/en/latest/specifications/entry-points/ .

- `[project.scripts]` maps to `console_scripts`; `[project.gui-scripts]` to `gui_scripts`.
- `[project.entry-points.console_scripts]` and `.gui_scripts` are reserved and forbidden by the spec.
- References use `module.path:object.qualname` with optional extras (extras discouraged).
- Names and reference shape are checked. Duplicate console/gui command names are flagged for review as an operational conflict.
- `MODULE_NOT_FOUND_LOCALLY` is an **inconclusive review heuristic**, not a build error. Backends can generate modules or different layouts; checks never import code.
- `PRIVATE_TARGET` is only a maintainability heuristic. No guarantees about object callability, dependency resolution or generated scripts.
