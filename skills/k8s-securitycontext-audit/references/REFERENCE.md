# Scope and references

- [Kubernetes Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/): container-level overrides, allowPrivilegeEscalation and seccomp.
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/): Restricted profiles require Linux capability drop ALL, non-root and compatible seccomp.
- **Important distinction:** `readOnlyRootFilesystem: true` is *additional hardening guidance*, not a Pod Security Standards Restricted requirement. This tool is not a PSS compliance engine.
- Policies can be affected by admission mutation, namespace settings, platform OS and runtime defaults that are outside input YAML. Supply **rendered** resources; Helm templates and Kustomize overlays are out of scope.
