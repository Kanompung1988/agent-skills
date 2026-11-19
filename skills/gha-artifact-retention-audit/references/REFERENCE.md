# Retention policy model and verification boundaries

This auditor checks `actions/upload-artifact` steps in local YAML. It never calls GitHub APIs. For each workflow step, numeric nonzero `retention-days` means the desired retention period; `0` (or omitted) selects repository default. Values with `${{ }}` are marked for manual review rather than being evaluated.

GitHub documents repository Actions retention settings and possible organization/enterprise limits, so **manually verify your effective policy** before acting on findings. Model defaults: 90 days maximum for artifacts in a public repository and 400 in private; these are platform modeling assumptions and should be checked against the actual host/current documentation.

The operator may provide `--policy-days N` and `--minimum-days N` as hypotheses; the analyzer reports conflicts with those supplied values. No policy is fetched or asserted. A 0/default configured value is explicitly treated as unknown unless the operator supplied the policy.

### Primary references

- [GitHub repository Actions retention settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [actions/upload-artifact README](https://github.com/actions/upload-artifact/blob/main/README.md)
- [GitHub 27 August 2026 notice on expanded Actions retention](https://github.blog/changelog/2026-08-27-actions-retention-will-cover-checks-workflow-runs-and-statuses/)
- [Agent Skills open specification](https://agentskills.io/specification)

### Non-goals

This tool does not validate the authenticity or trust of third-party actions, calculate workflow effective tokens, resolve referenced reusable workflows, fetch live repository settings, resolve expressions, delete/preserve old artifacts, or guarantee a legal retention term. It only checks selected `actions/upload-artifact` inputs from supplied files.
