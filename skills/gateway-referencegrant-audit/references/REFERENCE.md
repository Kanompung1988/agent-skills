# Review rules and scope

| Code | Meaning | Response |
|---|---|---|
| RG001 | Cross-namespace backend or TLS certificate reference has no matching local grant | Add a target-namespace ReferenceGrant or confirm separately in live manifests |
| RG002 | ReferenceGrant has an empty `from` or `to` list | Declare permitted source and destination |
| RG003 | `to` item lacks `group` or `kind` | Explicitly set target group ("" for Service/Secret) and kind |
| RG004 | Reference namespace is not a string | Correct manifest |
| RG005 | Cross-namespace ref has no target name | Correct manifest |

The analyser does not evaluate Service-parent mesh policy, Gateway AllowedRoutes, controller-specific extension references, Kubernetes API object validity, TLS secret contents or network health. A missing grant is scoped to the provided file set. Mirrors are included for HTTPRoute RequestMirror. For all routes, default backend `group` is core, `kind` is Service. Default certificate target is core Secret. Refer to current Gateway API spec before enabling broad grants.
