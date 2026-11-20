# Kubernetes Pod Security Admission Namespace Audit — evidence boundaries

Default `--minimum-enforce baseline` is an **operator policy** rather than an upstream Kubernetes requirement. Set `--minimum-enforce none` to disable that policy. `--require-pinned-version` is opt-in; `latest` is valid but may evolve with the cluster. An exemption flag only suppresses local review and does not configure a real cluster exemption.

## Official documentation

- https://kubernetes.io/docs/concepts/security/pod-security-admission/
- https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/

## False-positive and false-negative limits

This is a conservative single-file local manifest reviewer. Values can be dynamic and multiple overrides/cluster-level policy/Compose service activation behavior may change observed effects. It is not a deploy-time gate by itself. Interpret review findings manually and test the actual effective system with native official tools.

Input files are parsed through PyYAML SafeLoader with duplicate-mapping-key rejection and a 2MB limit. No dynamic evaluation is performed.
