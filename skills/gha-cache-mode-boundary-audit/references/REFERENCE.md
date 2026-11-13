# Cache trust boundary rules

- `CACHE_WRITE_LOW_TRUST`: explicit write or write-only on a potentially untrusted event; job-level overrides are respected.
- `CACHE_MODE_INVALID`: malformed or invalid static `cache-mode`.
- `CACHE_MODE_DYNAMIC`: cannot resolve expression-derived mode.
- `CACHE_STEPS_DISABLED`: cache step exists while mode is explicitly none.
- Omitted cache-mode is not flagged: GitHub enforces trigger-based defaults.
- Conservatively treat mixed-trust triggers as requiring review. A finding does **not** prove cache poisoning or code execution.
- Does not evaluate conditional jobs, shell scripts, runtime cache tokens, actual cached content or called-workflow privileges.
