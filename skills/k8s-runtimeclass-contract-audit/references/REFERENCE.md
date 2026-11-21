# Technical reference and boundaries

- Kubernetes RuntimeClass concepts: https://kubernetes.io/docs/concepts/containers/runtime-class/
- RuntimeClass API: https://kubernetes.io/docs/reference/kubernetes-api/node/runtime-class-v1/
- Pod overhead: https://kubernetes.io/docs/concepts/scheduling-eviction/pod-overhead/
- Agent Skills format: https://agentskills.io/specification

## Rules implemented

- A RuntimeClass requires a non-empty `spec.handler` and a cluster-scoped `metadata.name`.
- `spec.scheduling.nodeSelector` is merged with the Pod's `spec.nodeSelector`; if the same key has different values, admission rejects the Pod.
- RuntimeClass tolerations are appended to Pod tolerations (union semantics). This tool validates the field shape but does not attempt to model scheduler taint matching.
- `spec.overhead.podFixed` contains resource quantities associated with a Pod. This tool checks a conservative quantity lexical form and non-negative values only.
- Pod templates are inspected for Pod, Deployment, DaemonSet, StatefulSet, ReplicaSet, ReplicationController, Job and CronJob resources.

## Important limits

The tool does not query RuntimeClass objects outside the supplied files, discover supported nodes, prove handler installation, model every Kubernetes admission default, calculate scheduler resource fit, or validate the complete Kubernetes OpenAPI schema. An unresolved RuntimeClass reference is informational, not proof of absence. Run `kubectl apply --dry-run=server` against the intended cluster for authoritative API-server validation, and separately verify node/runtime readiness with the cluster operator.
