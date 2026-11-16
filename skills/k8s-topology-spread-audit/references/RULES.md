# Rules

- TS000: Malformed topology spread list/entry.
- TS001: Positive integer maxSkew required.
- TS002: Nonempty topologyKey required.
- TS003: whenUnsatisfiable must be DoNotSchedule or ScheduleAnyway.
- TS004: minDomains positive integer only with DoNotSchedule.
- TS005: nodeAffinityPolicy / nodeTaintsPolicy only Honor/Ignore.
- TS006: matchLabelKeys requires selector and label key list.
- TS007: Selector/matchLabelKeys name conflict.
- TS008: matchLabelKeys missing on pod template (review; admission may inject labels).
- TS009: Missing selector (review: cannot infer actual matching pods).
- TS010: Unsupported selector operator/shape.
- TS011: Label selector excludes own template (review, not always invalid).
- TS012: Duplicate constraint (review).

The tool cannot know eligible topology domains, actual workload placement, admission mutations or pod matching at runtime.
