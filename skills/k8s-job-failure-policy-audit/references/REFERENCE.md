# Technical reference and boundaries

- Kubernetes Job concepts and Pod failure policy: https://kubernetes.io/docs/concepts/workloads/controllers/job/
- Kubernetes Job API reference: https://kubernetes.io/docs/reference/kubernetes-api/batch/job-v1/
- Agent Skills specification: https://agentskills.io/specification

## Rules implemented

- `podFailurePolicy` requires Pod template `restartPolicy: Never`.
- When `podFailurePolicy` is set, an explicitly configured `podReplacementPolicy` must be `Failed`.
- Each rule must specify exactly one matcher: `onExitCodes` or `onPodConditions`.
- Exit-code operators are `In` or `NotIn`; values must be non-empty, unique, ordered non-negative integers. Exit code 0 is not valid with `In`.
- Optional `containerName` must identify a container or initContainer in the Pod template.
- Supported actions are `Count`, `Ignore`, `FailJob`, and `FailIndex`; `FailIndex` requires `backoffLimitPerIndex`.
- `backoffLimitPerIndex` requires Indexed completion and `restartPolicy: Never`. `maxFailedIndexes` requires `backoffLimitPerIndex` and cannot exceed a known `completions` value.
- When `backoffLimitPerIndex` is set and `backoffLimit` is omitted, Kubernetes defaults `backoffLimit` to 2147483647 rather than 6.

## Important limits

This tool does not evaluate every Kubernetes version/feature-gate combination, server-side default, controller state transition, Pod condition timing, or rule-shadowing interaction. It does not execute Jobs, contact clusters, inspect container exit behavior, or prove retries are idempotent. Use server-side dry-run against the target cluster and validate the application’s retry semantics with its owner.
