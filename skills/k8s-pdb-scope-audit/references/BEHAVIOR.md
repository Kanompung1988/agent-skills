# Behaviour and scope

**Source:** [Kubernetes: Specifying a Disruption Budget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/).

- For `policy/v1`, `{}` is a namespace-wide selector, whereas a null selector matches no Pods.
- `minAvailable` and `maxUnavailable` are mutually exclusive. Controller ownership and current Pod health are not known from these YAMLs.
- `OVERLAP` is inferred only from explicit **Pod** manifests in the same input and namespace; Deployment/ReplicaSet templates are not interpreted.
- `NO_PODS_IN_INPUT` is informational, not proof of a broken or unused PDB.
- Selector syntax is limited to Kubernetes matchLabels and standard matchExpressions. Unknown operators produce an uncertainty warning.
- PyYAML safe_load avoids Python object constructors; untrusted large/complex YAML may still be a resource hazard. File size limit: 2 MB.
- No cluster API calls, no kubectl, no mutation, no real-time `disruptionsAllowed`, and no server-side admission validation.
