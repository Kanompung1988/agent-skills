---
name: k8s-job-failure-policy-audit
description: Audit Kubernetes Job and CronJob retry contracts, podFailurePolicy rules, restartPolicy compatibility, backoffLimitPerIndex, FailIndex, pod replacement policy, and exit-code matchers. Use when reviewing batch/v1 Job or CronJob failure handling and retry behavior before deployment.
license: MIT
compatibility: Python 3.10+ and PyYAML 6.x; offline read-only YAML CLI; no cluster access required.
metadata:
  author: AREAZERO Skill Lab
  version: "1.0.0"
---

# Kubernetes Job Failure Policy Audit

## Trigger
Use when reviewing Kubernetes `batch/v1` Job or CronJob manifests that configure retries, `podFailurePolicy`, indexed completions, or replacement behavior.

Do not use as a live controller simulation, API-server schema validation, proof of application retry safety, or estimate of actual execution count/time.

## Procedure
1. Select only the user-authorized Job/CronJob YAML files or directory.
2. Install PyYAML in a disposable environment with `python -m pip install -r requirements.txt`.
3. Run `python scripts/audit.py <path-or-directory> --format json`.
4. Check `POD_FAILURE_POLICY_REQUIRES_NEVER`: a Job using `podFailurePolicy` must set the Pod template `restartPolicy: Never`.
5. Check `POD_REPLACEMENT_POLICY_INCOMPATIBLE`: when `podFailurePolicy` is used, `podReplacementPolicy` must be `Failed` if explicitly set.
6. Review exit-code matcher values, action names, referenced container/initContainer names, and the one-matcher-per-rule requirement. Rules are evaluated in order; first match wins. Do not reorder them without understanding intended precedence.
7. For indexed Jobs, verify `completionMode: Indexed`, `backoffLimitPerIndex`, `maxFailedIndexes`, and `FailIndex` together. Note the special default for `backoffLimit` when `backoffLimitPerIndex` is set.
8. Suggest a minimal patch, but never apply it or run cluster commands unless separately authorized. State all static-analysis limitations.

## Exit codes
- `0`: no findings at the configured threshold in supplied files.
- `2`: one or more findings at the configured threshold.
- `1`: invalid invocation or no YAML files.

## Examples
```bash
python scripts/audit.py fixtures/safe.yaml --format json
python scripts/audit.py fixtures/review.yaml --format json
python -m unittest discover -s tests -v
```
