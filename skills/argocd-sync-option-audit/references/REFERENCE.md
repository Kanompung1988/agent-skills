# Argo CD static sync review rules

| Code | Flag | Consequence to investigate |
|---|---|---|
| AO001 | Malformed option | Options require Key=value formatting |
| AO002 | Conflicting duplicate values | Last value may not be intended |
| AO003 | Replace=true | kubectl replace/create may be disruptive |
| AO004 | Replace + ServerSideApply | Replace takes precedence |
| AO005 | Force=true | May delete/recreate resources |
| AO006 | Validate=false | Kubernetes schema validation skipped |
| AO007 | SkipDryRunOnMissingResource=true | Dry-run safeguard skipped for missing kinds |
| AO008 | Prune=false | Orphaned resources remain |
| AO009 | Force with SSA without Replace | Force option alone ignored in SSA |
| AO010 | Automated prune and allowEmpty | Empty source may remove all managed objects |
| AO011 | ignoreDifferences without RespectIgnoreDifferences | Ignored differences may still be applied |

Rules are static review hints, not a complete Argo CD policy model. Resource-level overrides, AppProjects, sync windows, RBAC, destination health, and server behavior are not evaluated. Findings are advisory; human owners decide if the behavior is intentional.
