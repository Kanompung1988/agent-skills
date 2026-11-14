# HTTP semantic-convention migration rules

| Rule | Detection | Recommended review |
|---|---|---|
| OTEL_HTTP_LEGACY_KEYS | Legacy HTTP attribute keys appear outside declared http/dup mode | Map old names to stable semantics, update instrumentation and queries |
| OTEL_HTTP_DUAL_EMISSION | Old and stable paired keys coexist outside declared http/dup | Check intended stability rollout and duplicate costs |
| OTEL_HTTP_OPT_IN_CONFLICT | Old key appears despite declared stable-only http mode | Verify actual environment, SDK versions and instrumentation |
| OTEL_HTTP_ROUTE_CARDINALITY | http.route contains a UUID or long numeric path segment | Verify low-cardinality route template, do not emit raw IDs |

The old-to-new key mapping is selective and non-exhaustive. A missing route can be valid; the tool does not treat it as an automatic violation. Values are inspected only for route-shaped patterns and are never printed. Mixed emission may be intentional and is suppressed for a declared http/dup migration.
