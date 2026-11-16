# Rules

- HL001: Declared dependencies without Chart.lock.
- HL002: Duplicate declared name/repository identity.
- HL003: Declaration missing from lock.
- HL004: Lock-only identity.
- HL005: Lock entries with no declared dependencies.
- HL006: Missing dependency name.
- HL007: Missing version field.
- HL008: Missing repository (can be valid with vendored charts; advisory).
- HL009: Exact version mismatch (version ranges skipped).
- HL010: Missing/invalid digest format.
- HL011: Missing generated timestamp.

Exact name and repository comparisons are conservative; aliases, OCI repo normalization and charts/ vendoring may require manual review. Never claim proof of dependency authenticity from this audit.
