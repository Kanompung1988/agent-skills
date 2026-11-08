# Review rules and interpretation

VP001 unsupported admission API version; no interpretation attempted.
VP002 duplicate policy definition in the input bundle.
VP003 missing binding.policyName.
VP004 policyName not found **in the supplied bundle**; it may be in the live cluster.
VP005 missing/empty/unknown validationActions.
VP006 Deny plus Warn, an invalid combination.
VP007 Warn/Audit-only action; appropriate for rollout monitoring but **not** enforcement.
VP008 paramKind vs paramRef mismatch; absence of paramRef is a *review* signal, not a universal server-invalidity claim. paramRef is ignored if the policy has no paramKind.
VP009 paramRef must select exactly one of name or selector.
VP010 parameterNotFoundAction missing or unknown; required for paramRef.
VP011 parameterNotFoundAction=Allow means missing params are treated as successful validation.
VP012 policy has no binding **in the supplied YAML**, possibly intentional because another bundle provisions it.
VP013 failurePolicy Ignore does not reject evaluation errors; it can be intentional but review carefully.
VP014 matchConstraints without resourceRules should be reviewed for API validity.

The scanner only models a subset of admissionregistration.k8s.io/v1 local schema and binding relationships. It cannot evaluate CEL, matchConditions, effective namespace/objectSelector, cluster-scoped ParamKind, Kubernetes version gates, API defaulting, parameter object discovery or RBAC read permission. A clean report does not mean requests are actually denied. Review live admission API, policy rollout, and dry-runs separately. All file access is read-only, with capped local YAML file count/size and no symlink traversal.
