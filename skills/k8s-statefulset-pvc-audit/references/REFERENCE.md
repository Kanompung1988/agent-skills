# PVC retention review rules

- `PVC_DELETE_ON_SET_REMOVAL` and `PVC_DELETE_ON_SCALE_DOWN` prompt review of deliberate Delete policies.
- `PVC_POLICY_INVALID_VALUE`, `PVC_POLICY_UNKNOWN_FIELD`, `PVC_POLICY_MALFORMED` identify incorrect retention-policy declarations.
- `PVC_TEMPLATE_UNNAMED`, `PVC_TEMPLATE_DUPLICATE`, `PVC_TEMPLATE_INVALID`, `PVC_STORAGE_REQUEST_MISSING` validate claim-template consistency.
- `PVC_POLICY_WITHOUT_TEMPLATES`: policy has no generated templates to govern.
- `STS_VERSION_REVIEW`: implementation targets apps/v1. Omitted policy means Retain; do not flag as data loss.
- Does not predict PersistentVolume reclaim behavior, Helm/Kustomize rendering, backups or effective live-controller settings.
