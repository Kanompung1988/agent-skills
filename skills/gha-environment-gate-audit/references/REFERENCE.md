# Rules and confidence boundaries

- `ENV001` — deployment-like job name but no environment; name heuristic only.
- `ENV002` — unsupported environment mapping or empty name.
- `ENV003` — dynamic `${{ ... }}` environment name, requires manual resolution.
- `ENV004` — no inventory supplied; unknown effective protection, informational.
- `ENV005` — environment missing in supplied inventory; may be created without gates.
- `ENV006` — inventory does not affirm at least one required reviewer.
- `ENV007` — self-review prevention is not recorded true; informational, optional hardening.
- `ENV008` — administrative bypass restriction not recorded false; informational.
- `ENV009` — deployment branch/tag restrictions not recorded enabled.

**Inventory schema:** `examples/inventory.json` is hypothetical, not fetched from GitHub. Fields are `environments.<name>.required_reviewers` (integer count), `prevent_self_review` (boolean), `can_admins_bypass` (boolean), `deployment_branch_policy.protected_branches` / `custom_branch_policies` (booleans). Case-folded environment names. Respect GitHub plan-specific availability. The supplied inventory can become stale; check actual Settings → Environments before relying on release gates. No source commands/secrets printed.
