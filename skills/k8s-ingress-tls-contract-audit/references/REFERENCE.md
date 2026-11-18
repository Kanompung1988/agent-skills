# Technical reference and boundaries

Kubernetes Ingress: https://kubernetes.io/docs/concepts/services-networking/ingress/
Ingress API: https://kubernetes.io/docs/reference/kubernetes-api/networking/ingress-v1/

Check networking.k8s.io/v1 Ingress resources and supplied Secret metadata from the same namespace. A Secret omitted from the local batch is a review finding, never proof that it does not exist in the cluster. Optional `secretName` may intentionally rely on controller-specific TLS behavior, also review-only. Missing or wrong Secret type/keys is an error when Secret included. Host mismatch is flagged for review; wildcard matching and controller implementation require human confirmation. The tool does not verify certificate SAN, PEM, expiry, chain, actual cluster state or TLS handshakes. Inputs may contain sensitive values even though the tool never reports them; use redacted/synthetic YAML.
