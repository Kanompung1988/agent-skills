# Static Node.js exports review model

Reviewed 2026-11-01. Primary Node.js docs: https://nodejs.org/api/packages.html (Subpath exports, conditional exports, path rules and validation for export targets). npm reference: https://docs.npmjs.com/cli/v11/configuring-npm/package-json/#exports

`exports` values may be a single target string, null (intentionally blocked), array fallback, or nested subpath/condition maps. Every non-null path target must start `./` and cannot traverse outside the package root, contain dot/dot-dot or `node_modules` path components. Mixed subpath keys and condition keys in the same object are invalid. The scanner reports those structural issues but does not implement Node package target resolution or the full URL/percent-decoding grammar.

A pattern target or key is reported as REVIEW and deliberately not expanded. When `--check-files` is set, non-pattern local target existence is checked; missing files are REVIEW because TypeScript and other builds generate distribution files after compilation. The tool refuses package.json input symlinks and rejects duplicate JSON keys. It does not execute JavaScript, npm scripts or any network access.
