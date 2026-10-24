# Security policy

These skills are read-only local analyzers, not security audit products. The code does not fetch remote schemas, execute commands found in CI logs or request API credentials.

## Handling sensitive information

- Use synthetic fixtures when filing GitHub issues or PRs.
- Do not upload unreviewed CI logs containing credentials, tokens or personally identifying information.
- CI triage uses best-effort pattern redaction; it does **not** guarantee complete removal of secrets.
- OpenAPI specs can reveal internal topology or endpoints; use an appropriate private workspace and your organization's data policy.
- Read scripts before running them. Limit access to local inputs and report paths.

## Reporting suspected vulnerabilities

For a security issue, avoid including live credentials or exploit payloads in public GitHub issues. Contact the repository owner through GitHub account contact options or use GitHub's private vulnerability reporting feature **if enabled**. We do not claim an SLA for external security reports.

Supported version: `main` and latest published code only. Historical snapshots may not receive security patches.
