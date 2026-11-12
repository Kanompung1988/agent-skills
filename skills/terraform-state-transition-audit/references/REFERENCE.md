# Rules and confidence boundaries

- `TFM001` — missing `from` or `to` in moved block.
- `TFM002` — unsupported static address syntax; not evidence of invalid Terraform.
- `TFM003` — no-op source = target.
- `TFM004` — repeated move source.
- `TFM005` — multiple old addresses targeting the same destination.
- `TFM006` — cycle in the static move graph (chained moves *without* cycles are valid).
- `TFR001` — removed block missing `from`.
- `TFR002` — unsupported removed address syntax, manual review.
- `TFR003` — removed block does not explicitly set `lifecycle { destroy = false }`. This is a **risk check for non-destructive handoffs**, not a claim that destroy=true is invalid Terraform.
- `TFR004` — repeated removed address.
- `TFR005` — removed address overlaps with a moved source or target.

Input is an HCL **lexical subset**, not a full HCL parser. The scanner masks quoted strings, line/block comments and heredocs to reduce false positives. It does not resolve resources in state, module expansions, `count`, `for_each`, workspace names, plan effects, or provider operations. Perform `terraform fmt -check`, `terraform validate`, and a reviewed `terraform plan` with the intended backend before any apply. Terraform 1.7+ supports `removed` blocks; verify target version.
