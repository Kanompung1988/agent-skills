# Model and references

Reviewed 2026-11-01. Primary source: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html (AWS recommends narrowing GitHub OIDC trust by repository/branch). GitHub context: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws.

The scanner identifies a JSON trust-policy `Statement` with `Effect=Allow`, a GitHub OIDC `Principal.Federated` ARN, and an `Action` of `sts:AssumeRoleWithWebIdentity` or wildcard. It recognizes only positive `StringEquals` or `StringLike` restrictions on the GitHub `sub` and `aud` condition keys. It conservatively flags unsupported positive/negative operators for manual assessment. IAM allows OR behavior within condition value arrays, so any broad matching value is flagged.

Scope intentionally excludes AWS evaluation logic and conditions unrelated to GitHub `sub` and `aud`; a HIGH finding means risky *static configuration*, not a confirmed exploit. Environment subjects must be reviewed against GitHub environment branch restrictions and required reviewers.

Input should be a redacted export of the **role trust policy**, not credentials, access keys or permission documents. The tool does not transmit or print condition values. No network access or AWS credentials are used.
